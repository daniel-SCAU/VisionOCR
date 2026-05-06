// VisionOCR global utilities
window.VisionOCR = {
    formatDate: function(ts) {
        return new Date(ts).toLocaleString();
    },
    statusClass: function(status) {
        if (status === 'PASS') return 'text-success';
        if (status === 'FAIL') return 'text-danger';
        return 'text-warning';
    }
};
