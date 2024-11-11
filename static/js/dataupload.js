document.addEventListener('DOMContentLoaded', function () {
    const fileUploadField = document.querySelector('.file-upload-field');
    const fileUploadWrapper = document.querySelector('.file-upload-wrapper');

    fileUploadField.addEventListener('change', function () {
        if (fileUploadField.files.length > 0) {
            const fileName = fileUploadField.files[0].name;
            fileUploadWrapper.setAttribute('data-text', fileName);
        }
    });
});
