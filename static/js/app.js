// Secure Image Gallery Client — Sahana
// AWS EC2 & S3 Object Storage Project

let currentImages = [];
let displayedImages = [];
let currentRole = localStorage.getItem('sahana_iam_role') || 'ImageAdmins';
let activeKeyForPresign = null;
let activeLightboxIndex = -1;
let presignCountdownInterval = null;

document.addEventListener('DOMContentLoaded', () => {
  initIcons();
  applyRoleUI();
  loadStats();
  loadImages();
  setupEventListeners();
});

function initIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

// ---------------- ROLE-BASED ACCESS CONTROL (RBAC) ----------------
function setRole(role) {
  currentRole = role;
  localStorage.setItem('sahana_iam_role', role);
  applyRoleUI();
  showToast(`Active IAM Role switched to: ${role}`, 'info');
}

function applyRoleUI() {
  const adminBtn = document.getElementById('role-admin-btn');
  const viewerBtn = document.getElementById('role-viewer-btn');

  if (currentRole === 'ImageAdmins') {
    adminBtn.className = 'px-2.5 py-1 rounded-lg font-medium transition bg-indigo-600 text-white shadow-sm flex items-center gap-1';
    viewerBtn.className = 'px-2.5 py-1 rounded-lg font-medium transition text-slate-400 hover:text-slate-200 flex items-center gap-1';
  } else {
    viewerBtn.className = 'px-2.5 py-1 rounded-lg font-medium transition bg-amber-600 text-white shadow-sm flex items-center gap-1';
    adminBtn.className = 'px-2.5 py-1 rounded-lg font-medium transition text-slate-400 hover:text-slate-200 flex items-center gap-1';
  }
}

// ---------------- SETUP EVENT LISTENERS ----------------
function setupEventListeners() {
  // File input change
  const fileInput = document.getElementById('file-input');
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Drag and drop setup
  const dropzone = document.getElementById('upload-container');
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files[0]) {
      handleFileUpload(files[0]);
    }
  });

  // Search input
  document.getElementById('search-input').addEventListener('input', () => {
    applySortAndFilter();
  });

  // Pre-Signed URL buttons
  document.getElementById('generate-presign-btn').addEventListener('click', () => {
    generatePresignedUrl();
  });

  document.getElementById('copy-presign-btn').addEventListener('click', () => {
    copyPresignedUrl();
  });

  // Keyboard navigation for lightbox
  document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('lightbox-modal');
    if (!modal.classList.contains('hidden')) {
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowLeft') navigateLightbox(-1);
      if (e.key === 'ArrowRight') navigateLightbox(1);
    }
  });
}

function toggleUploadDropzone(forceState = null) {
  const container = document.getElementById('upload-container');
  if (!container) return;
  if (forceState === true) {
    container.classList.remove('hidden');
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });
  } else if (forceState === false) {
    container.classList.add('hidden');
  } else {
    container.classList.toggle('hidden');
    if (!container.classList.contains('hidden')) {
      container.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  initIcons();
}

// ---------------- LOAD STATS & METRICS ----------------
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (data.success && data.stats) {
      const s = data.stats;
      document.getElementById('stat-total-images').textContent = s.total_images;
      document.getElementById('stat-storage-used').textContent = s.total_bytes_formatted || formatBytes(s.total_bytes);
      document.getElementById('stat-total-versions').textContent = `${s.total_versions || s.total_images} Versions`;

      if (s.last_upload) {
        document.getElementById('stat-latest-file').textContent = s.last_upload.key;
        document.getElementById('stat-latest-time').textContent = s.last_upload.last_modified;
      } else {
        document.getElementById('stat-latest-file').textContent = 'None yet';
        document.getElementById('stat-latest-time').textContent = 'Bucket empty';
      }
    }
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

// ---------------- LOAD & RENDER IMAGES ----------------
async function loadImages() {
  try {
    const res = await fetch('/api/images');
    const data = await res.json();

    if (data.success) {
      currentImages = data.images;
      applySortAndFilter();
    }
  } catch (err) {
    console.error('Failed to load images:', err);
    showToast('Failed to load images from S3 storage', 'error');
  }
}

function applySortAndFilter() {
  const query = document.getElementById('search-input').value.trim().toLowerCase();
  const sortType = document.getElementById('sort-select').value;

  let filtered = currentImages.filter(img => img.key.toLowerCase().includes(query));

  filtered.sort((a, b) => {
    if (sortType === 'newest') {
      return new Date(b.last_modified) - new Date(a.last_modified);
    } else if (sortType === 'oldest') {
      return new Date(a.last_modified) - new Date(b.last_modified);
    } else if (sortType === 'name_asc') {
      return a.key.localeCompare(b.key);
    } else if (sortType === 'name_desc') {
      return b.key.localeCompare(a.key);
    } else if (sortType === 'size_desc') {
      return (b.size || 0) - (a.size || 0);
    } else if (sortType === 'size_asc') {
      return (a.size || 0) - (b.size || 0);
    }
    return 0;
  });

  displayedImages = filtered;
  renderGallery(displayedImages);
}

function renderGallery(images) {
  const grid = document.getElementById('gallery-grid');
  const emptyState = document.getElementById('empty-state');
  const countBadge = document.getElementById('gallery-count');

  countBadge.textContent = `Showing ${images.length} of ${currentImages.length} objects`;

  if (images.length === 0) {
    grid.innerHTML = '';
    emptyState.classList.remove('hidden');
    emptyState.classList.add('flex');
    return;
  }

  emptyState.classList.add('hidden');
  emptyState.classList.remove('flex');
  grid.innerHTML = '';

  images.forEach((img, idx) => {
    const card = document.createElement('div');
    card.className = 'group bg-slate-900 border border-slate-800/90 hover:border-slate-700 rounded-2xl overflow-hidden card-hover-effect flex flex-col shadow-sm transition';

    const formattedSize = formatBytes(img.size);
    const versionCount = img.total_versions || 1;

    card.innerHTML = `
      <!-- Thumbnail & Preview -->
      <div class="relative aspect-[4/3] bg-slate-950 overflow-hidden cursor-pointer" onclick="openLightboxByIndex(${idx})">
        <img src="${img.preview_url}" alt="${escapeHtml(img.key)}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" loading="lazy">
        
        <!-- Version ID Badge -->
        <div class="absolute top-2.5 left-2.5 z-10">
          <span class="px-2 py-0.5 rounded-md bg-slate-950/80 backdrop-blur-md border border-slate-800 text-[10px] text-emerald-400 font-mono flex items-center gap-1 shadow-sm">
            <i data-lucide="tag" class="w-2.5 h-2.5"></i>
            <span>${escapeHtml(img.version_id ? img.version_id.substring(0, 8) : 'v1')}</span>
          </span>
        </div>

        <!-- Hover Overlay -->
        <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition duration-200 flex items-end justify-between p-3">
          <span class="text-xs text-white font-medium flex items-center gap-1.5">
            <i data-lucide="maximize-2" class="w-3.5 h-3.5"></i> Preview &amp; Info
          </span>
          <span class="text-[11px] text-slate-300 font-mono">${formattedSize}</span>
        </div>
      </div>

      <!-- Card Details & Actions -->
      <div class="p-3.5 flex-1 flex flex-col justify-between">
        <div>
          <h4 class="text-xs sm:text-sm font-semibold text-slate-200 truncate font-mono" title="${escapeHtml(img.key)}">${escapeHtml(img.key)}</h4>
          <div class="flex items-center justify-between text-[11px] text-slate-400 mt-1">
            <span>${formattedSize}</span>
            <span>${img.last_modified.split(' ')[0]}</span>
          </div>
        </div>

        <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between gap-1.5 text-xs">
          <!-- Generate Pre-Signed URL -->
          <button onclick="openPresignModal('${escapeHtml(img.key)}')" title="Generate temporary Pre-Signed URL" class="px-2 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 font-medium transition flex items-center gap-1">
            <i data-lucide="link" class="w-3 h-3"></i>
            <span class="hidden sm:inline">Share URL</span>
          </button>

          <!-- S3 Versions History -->
          <button onclick="openVersionsModal('${escapeHtml(img.key)}')" title="View S3 object versions & restore" class="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition flex items-center gap-1">
            <i data-lucide="history" class="w-3 h-3 text-sky-400"></i>
            <span>Versions (${versionCount})</span>
          </button>

          <!-- Delete Action (RBAC-enforced) -->
          <button onclick="deleteImage('${escapeHtml(img.key)}')" title="Delete from Object Storage" class="p-1 rounded-lg hover:bg-rose-500/10 text-slate-400 hover:text-rose-400 transition">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
    `;

    grid.appendChild(card);
  });

  initIcons();
}

// ---------------- FILE UPLOAD & VALIDATION ----------------
async function handleFileUpload(file) {
  const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
  const ext = file.name.split('.').pop().toLowerCase();

  // 1. Format validation
  if (!allowedExtensions.includes(ext)) {
    showToast(`Invalid file type (.${ext}). Allowed: JPG, PNG, WEBP, GIF`, 'error');
    return;
  }

  // 2. Size validation (15 MB)
  const maxBytes = 15 * 1024 * 1024;
  if (file.size > maxBytes) {
    showToast(`File exceeds 15 MB limit (${formatBytes(file.size)})`, 'error');
    return;
  }

  // Show Progress UI
  const statusBox = document.getElementById('upload-status-box');
  const filenameText = document.getElementById('upload-filename-text');
  const percentText = document.getElementById('upload-percent-text');
  const progressBar = document.getElementById('upload-progress-bar');

  statusBox.classList.remove('hidden');
  filenameText.textContent = `Uploading ${file.name} (${formatBytes(file.size)})...`;
  progressBar.style.width = '30%';
  percentText.textContent = '30%';

  const formData = new FormData();
  formData.append('image', file);

  try {
    progressBar.style.width = '65%';
    percentText.textContent = '65%';

    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: {
        'X-User-Role': currentRole
      },
      body: formData
    });
    const data = await res.json();

    progressBar.style.width = '100%';
    percentText.textContent = '100%';

    if (data.success) {
      showToast(`Uploaded "${file.name}" to Amazon S3 (Version: ${data.data.version_id})`, 'success');
      document.getElementById('file-input').value = '';
      await loadStats();
      await loadImages();
    } else {
      showToast(data.error || 'Upload failed', 'error');
    }
  } catch (err) {
    showToast('Network error during upload to S3', 'error');
  } finally {
    setTimeout(() => {
      statusBox.classList.add('hidden');
      progressBar.style.width = '0%';
      percentText.textContent = '0%';
      toggleUploadDropzone(false);
    }, 1200);
  }
}

// ---------------- PUBLIC APIS INGESTION (public-apis) ----------------
async function importPublicApi(source) {
  const statusBox = document.getElementById('upload-status-box');
  const filenameText = document.getElementById('upload-filename-text');
  const percentText = document.getElementById('upload-percent-text');
  const progressBar = document.getElementById('upload-progress-bar');

  statusBox.classList.remove('hidden');
  const sourceName = source === 'nasa' ? 'NASA APOD API' : source === 'picsum' ? 'Picsum Curated API' : 'Dog CEO Animals API';
  filenameText.textContent = `Streaming from ${sourceName} into Amazon S3...`;
  progressBar.style.width = '35%';
  percentText.textContent = '35%';

  try {
    progressBar.style.width = '70%';
    percentText.textContent = '70%';

    const res = await fetch('/api/public-apis/import', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Role': currentRole
      },
      body: JSON.stringify({ source: source })
    });
    const data = await res.json();

    progressBar.style.width = '100%';
    percentText.textContent = '100%';

    if (data.success) {
      showToast(`Ingested ${data.data.key} from Public API into S3! (Version: ${data.data.version_id})`, 'success');
      await loadStats();
      await loadImages();
    } else {
      showToast(data.error || 'Public API ingestion failed', 'error');
    }
  } catch (err) {
    showToast('Network error during Public API ingestion', 'error');
  } finally {
    setTimeout(() => {
      statusBox.classList.add('hidden');
      progressBar.style.width = '0%';
      percentText.textContent = '0%';
      toggleUploadDropzone(false);
    }, 1200);
  }
}

// ---------------- DELETE IMAGE (RBAC ENFORCED) ----------------
async function deleteImage(key, versionId = null) {
  // If user role is Viewer, demonstrate Least Privilege enforcement in UI
  if (currentRole === 'Viewer') {
    showToast('Access Denied (403): User lacks s3:DeleteObject permission. Restricted to IAM group "ImageAdmins" (Least Privilege Principle)', 'error');
    return;
  }

  const promptMsg = versionId 
    ? `Permanently delete specific S3 version (${versionId}) of "${key}"?` 
    : `Delete "${key}" from S3 bucket? (Bucket Versioning will record a Delete Marker)`;

  if (!confirm(promptMsg)) return;

  try {
    const url = versionId 
      ? `/api/images/${encodeURIComponent(key)}?version_id=${encodeURIComponent(versionId)}`
      : `/api/images/${encodeURIComponent(key)}`;

    const res = await fetch(url, { 
      method: 'DELETE',
      headers: {
        'X-User-Role': currentRole
      }
    });
    const data = await res.json();

    if (data.success) {
      showToast('Object deleted successfully from S3', 'success');
      await loadStats();
      await loadImages();
    } else {
      showToast(data.error || 'Deletion failed', 'error');
    }
  } catch (err) {
    showToast('Failed to delete object from storage', 'error');
  }
}

// ---------------- S3 OBJECT VERSIONS & RESTORE ----------------
async function openVersionsModal(key) {
  document.getElementById('version-modal-filename').textContent = `(${key})`;
  const tableBody = document.getElementById('versions-table-body');
  tableBody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-500">Loading versions from S3...</td></tr>';

  const modal = document.getElementById('versions-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  initIcons();

  try {
    const res = await fetch(`/api/images/${encodeURIComponent(key)}/versions`);
    const data = await res.json();

    if (data.success && data.versions) {
      tableBody.innerHTML = '';
      if (data.versions.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-500">No versions found</td></tr>';
        return;
      }

      data.versions.forEach(v => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';

        const isLatest = v.is_latest;
        const isDeleteMarker = v.is_delete_marker;
        
        let statusBadge = '';
        if (isDeleteMarker) {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px]">Delete Marker</span>';
        } else if (isLatest) {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">Current Version</span>';
        } else {
          statusBadge = '<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">Historical Version</span>';
        }

        const sizeText = isDeleteMarker ? '-' : formatBytes(v.size);
        const actionHtml = isDeleteMarker 
          ? `<button onclick="deleteImage('${escapeHtml(key)}', '${v.version_id}'); closeVersionsModal();" class="text-rose-400 hover:text-rose-300 text-[11px] underline">Remove Marker</button>`
          : isLatest
          ? `<a href="${v.preview_url}" target="_blank" class="text-indigo-400 hover:text-indigo-300 text-[11px] underline">View Current</a>`
          : `<div class="flex items-center justify-end gap-2">
              <a href="${v.preview_url}" target="_blank" class="text-slate-400 hover:text-slate-200 text-[11px] underline">View</a>
              <button onclick="restoreVersion('${escapeHtml(key)}', '${v.version_id}')" class="px-2 py-0.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-sans font-medium transition">Restore</button>
            </div>`;

        tr.innerHTML = `
          <td class="py-2.5 text-indigo-400 font-bold">${escapeHtml(v.version_id)}</td>
          <td class="py-2.5 text-slate-300">${v.uploaded_at || v.last_modified}</td>
          <td class="py-2.5 text-slate-400">${sizeText}</td>
          <td class="py-2.5">${statusBadge}</td>
          <td class="py-2.5 text-right">${actionHtml}</td>
        `;
        tableBody.appendChild(tr);
      });
      initIcons();
    }
  } catch (err) {
    tableBody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-rose-400">Failed to load versions</td></tr>';
  }
}

function closeVersionsModal() {
  const modal = document.getElementById('versions-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

async function restoreVersion(key, versionId) {
  if (currentRole === 'Viewer') {
    showToast('Access Denied (403): User lacks s3:PutObject restore permissions. Restricted to ImageAdmins (Least Privilege)', 'error');
    return;
  }

  try {
    const res = await fetch(`/api/images/${encodeURIComponent(key)}/versions/${encodeURIComponent(versionId)}/restore`, {
      method: 'POST',
      headers: { 'X-User-Role': currentRole }
    });
    const data = await res.json();

    if (data.success) {
      showToast(`Restored version ${versionId} as current active version`, 'success');
      closeVersionsModal();
      await loadStats();
      await loadImages();
    } else {
      showToast(data.error || 'Failed to restore version', 'error');
    }
  } catch (err) {
    showToast('Error restoring version', 'error');
  }
}

// ---------------- LIGHTBOX MODAL & S3 METADATA INSPECTOR ----------------
function openLightboxByIndex(index) {
  if (index < 0 || index >= displayedImages.length) return;
  activeLightboxIndex = index;
  const img = displayedImages[index];

  document.getElementById('modal-image-title').textContent = img.key;
  document.getElementById('modal-image-preview').src = img.preview_url;
  
  // Download button
  const dlBtn = document.getElementById('modal-download-btn');
  dlBtn.href = img.preview_url;
  dlBtn.setAttribute('download', img.key);

  // Share button
  document.getElementById('modal-share-btn').onclick = () => {
    closeLightbox();
    openPresignModal(img.key);
  };

  // Footer meta strip
  document.getElementById('modal-image-meta-strip').innerHTML = `
    <span>${formatBytes(img.size)}</span> • <span>${img.last_modified}</span> • <span>Version: ${img.version_id ? img.version_id.substring(0, 8) : 'v1'}</span>
  `;

  // Fetch full S3 Object Metadata
  loadObjectMetadata(img.key);

  const modal = document.getElementById('lightbox-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  initIcons();
}

async function loadObjectMetadata(key) {
  try {
    const res = await fetch(`/api/images/${encodeURIComponent(key)}/metadata`);
    const data = await res.json();
    if (data.success) {
      document.getElementById('meta-key').textContent = data.key;
      document.getElementById('meta-bucket').textContent = data.bucket;
      document.getElementById('meta-version').textContent = data.version_id;
      document.getElementById('meta-size').textContent = `${data.size} bytes (${formatBytes(data.size)})`;
      document.getElementById('meta-type').textContent = data.content_type;
      document.getElementById('meta-time').textContent = data.uploaded_at;
    }
  } catch (e) {
    console.error('Failed to load metadata:', e);
  }
}

function navigateLightbox(direction) {
  if (displayedImages.length <= 1) return;
  let newIndex = activeLightboxIndex + direction;
  if (newIndex < 0) newIndex = displayedImages.length - 1;
  if (newIndex >= displayedImages.length) newIndex = 0;
  openLightboxByIndex(newIndex);
}

function toggleMetadataDrawer() {
  const drawer = document.getElementById('metadata-drawer');
  drawer.classList.toggle('hidden');
}

function closeLightbox() {
  const modal = document.getElementById('lightbox-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  activeLightboxIndex = -1;
}

// ---------------- PRE-SIGNED URL GENERATOR MODAL ----------------
function openPresignModal(key) {
  activeKeyForPresign = key;
  document.getElementById('presign-target-key').value = key;
  document.getElementById('presign-result').classList.add('hidden');
  clearInterval(presignCountdownInterval);
  
  const modal = document.getElementById('presign-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  initIcons();
}

function closePresignModal() {
  const modal = document.getElementById('presign-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  activeKeyForPresign = null;
  clearInterval(presignCountdownInterval);
}

async function generatePresignedUrl() {
  if (!activeKeyForPresign) return;
  const expiry = document.getElementById('presign-expiry').value;

  try {
    const res = await fetch(`/api/images/${encodeURIComponent(activeKeyForPresign)}/presign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expires_in: parseInt(expiry) })
    });
    const data = await res.json();

    if (data.success && data.data) {
      const result = data.data;
      const fullUrl = result.url.startsWith('http') ? result.url : window.location.origin + result.url;
      
      document.getElementById('presign-url-output').value = fullUrl;
      document.getElementById('presign-test-link').href = fullUrl;
      document.getElementById('presign-result').classList.remove('hidden');
      
      // Start live countdown timer
      startCountdownTimer(parseInt(expiry));

      initIcons();
      showToast('Temporary Pre-Signed URL generated!', 'success');
    } else {
      showToast(data.error || 'Failed to generate URL', 'error');
    }
  } catch (err) {
    showToast('Network error generating URL', 'error');
  }
}

function startCountdownTimer(seconds) {
  clearInterval(presignCountdownInterval);
  let remaining = seconds;
  const badge = document.getElementById('presign-countdown-badge');

  function update() {
    if (remaining <= 0) {
      badge.textContent = 'Expired';
      badge.className = 'font-mono bg-rose-500/20 text-rose-400 px-2 py-0.5 rounded text-[11px]';
      clearInterval(presignCountdownInterval);
      return;
    }

    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    badge.textContent = `Valid: ${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    badge.className = 'font-mono bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-[11px]';
    remaining--;
  }

  update();
  presignCountdownInterval = setInterval(update, 1000);
}

function copyPresignedUrl() {
  const input = document.getElementById('presign-url-output');
  input.select();
  navigator.clipboard.writeText(input.value);

  const btnText = document.getElementById('copy-btn-text');
  btnText.textContent = 'Copied!';
  setTimeout(() => {
    btnText.textContent = 'Copy';
  }, 2000);

  showToast('Copied Pre-Signed URL to clipboard', 'success');
}

// ---------------- TOAST NOTIFICATION HELPER ----------------
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');

  const bgClass = type === 'success' 
    ? 'bg-slate-900 border-emerald-500/50 text-emerald-300' 
    : type === 'error' 
    ? 'bg-slate-900 border-rose-500/50 text-rose-300' 
    : 'bg-slate-900 border-indigo-500/50 text-indigo-300';

  const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info';

  toast.className = `pointer-events-auto flex items-center gap-2.5 px-4 py-3 rounded-xl border shadow-2xl text-xs transition duration-300 transform translate-y-2 opacity-0 max-w-md ${bgClass}`;
  toast.innerHTML = `
    <i data-lucide="${iconName}" class="w-4 h-4 shrink-0"></i>
    <span class="leading-relaxed">${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);
  initIcons();

  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-x-4');
    setTimeout(() => toast.remove(), 350);
  }, 4500);
}

function formatBytes(bytes) {
  if (bytes === 0 || !bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function escapeHtml(text) {
  if (typeof text !== 'string') return text;
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
