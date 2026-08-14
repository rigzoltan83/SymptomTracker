document.addEventListener(
    "DOMContentLoaded",
    () => {
        const i18n =
            window.FOOD_IMAGE_I18N || {};

        const cameraInput =
            document.getElementById(
                "food-camera-input"
            );

        const galleryInput =
            document.getElementById(
                "food-gallery-input"
            );

        const preview =
            document.getElementById(
                "food-image-preview"
            );

        const count =
            document.getElementById(
                "food-image-count"
            );

        const form =
            cameraInput
                ? cameraInput.closest("form")
                : null;

        if (
            !cameraInput
            || !galleryInput
            || !preview
            || !form
        ) {
            return;
        }


        const MAX_DIMENSION = 1800;
        const JPEG_QUALITY = 0.82;

        const selectedFiles = [];

        let processingCount = 0;


        function formatBytes(bytes) {
            if (bytes < 1024) {
                return `${bytes} B`;
            }

            if (bytes < 1024 * 1024) {
                return (
                    `${(
                        bytes / 1024
                    ).toFixed(0)} KB`
                );
            }

            return (
                `${(
                    bytes
                    / 1024
                    / 1024
                ).toFixed(1)} MB`
            );
        }


        function makeJpegFilename(
            originalName
        ) {
            const base =
                originalName
                    .replace(
                        /\.[^.]+$/,
                        ""
                    )
                    .replace(
                        /[^a-zA-Z0-9_-]+/g,
                        "_"
                    );

            return (
                `${base || "photo"}.jpg`
            );
        }


        function updateStatus() {
            if (!count) {
                return;
            }

            if (processingCount > 0) {
                count.textContent =
                    (i18n.processing || "Processing images…");

                return;
            }

            if (
                selectedFiles.length === 0
            ) {
                count.textContent = "";

                return;
            }

            const totalBytes =
                selectedFiles.reduce(
                    (sum, file) =>
                        sum + file.size,
                    0
                );

            count.textContent =
                (
                    i18n.count
                        ? i18n.count.replace(
                            "{count}",
                            selectedFiles.length
                        )
                        : `${selectedFiles.length} image(s)`
                )
                + " · "
                + formatBytes(totalBytes);
        }


        function loadImage(file) {
            return new Promise(
                (resolve, reject) => {
                    const url =
                        URL.createObjectURL(
                            file
                        );

                    const image =
                        new Image();

                    image.onload = () => {
                        URL.revokeObjectURL(
                            url
                        );

                        resolve(image);
                    };

                    image.onerror = () => {
                        URL.revokeObjectURL(
                            url
                        );

                        reject(
                            new Error(
                                (i18n.unreadable || "The image cannot be read.")
                            )
                        );
                    };

                    image.src = url;
                }
            );
        }


        async function compressImage(
            file
        ) {
            const image =
                await loadImage(file);

            let width =
                image.naturalWidth;

            let height =
                image.naturalHeight;

            if (
                width > MAX_DIMENSION
                || height > MAX_DIMENSION
            ) {
                const scale =
                    Math.min(
                        MAX_DIMENSION / width,
                        MAX_DIMENSION / height
                    );

                width =
                    Math.round(
                        width * scale
                    );

                height =
                    Math.round(
                        height * scale
                    );
            }

            const canvas =
                document.createElement(
                    "canvas"
                );

            canvas.width = width;
            canvas.height = height;

            const context =
                canvas.getContext("2d");

            if (!context) {
                throw new Error(
                    (i18n.processingFailed || "The image cannot be processed.")
                );
            }

            context.drawImage(
                image,
                0,
                0,
                width,
                height
            );

            const blob =
                await new Promise(
                    (resolve, reject) => {
                        canvas.toBlob(
                            result => {
                                if (!result) {
                                    reject(
                                        new Error(
                                            (i18n.compressionFailed || "Image compression failed.")
                                        )
                                    );

                                    return;
                                }

                                resolve(result);
                            },
                            "image/jpeg",
                            JPEG_QUALITY
                        );
                    }
                );

            return new File(
                [blob],
                makeJpegFilename(
                    file.name
                ),
                {
                    type: "image/jpeg",
                    lastModified:
                        Date.now(),
                }
            );
        }


        function renderPreview() {
            preview.innerHTML = "";

            selectedFiles.forEach(
                (file, index) => {
                    const wrapper =
                        document.createElement(
                            "div"
                        );

                    wrapper.className =
                        "upload-preview-item";


                    const image =
                        document.createElement(
                            "img"
                        );

                    image.alt =
                        (i18n.selectedFood || "Selected food image");

                    const url =
                        URL.createObjectURL(
                            file
                        );

                    image.src = url;

                    image.addEventListener(
                        "load",
                        () => {
                            URL.revokeObjectURL(
                                url
                            );
                        },
                        {
                            once: true,
                        }
                    );


                    const remove =
                        document.createElement(
                            "button"
                        );

                    remove.type = "button";

                    remove.className =
                        "upload-preview-remove";

                    remove.textContent = "×";

                    remove.setAttribute(
                        "aria-label",
                        (i18n.remove || "Remove image")
                    );

                    remove.addEventListener(
                        "click",
                        () => {
                            selectedFiles.splice(
                                index,
                                1
                            );

                            renderPreview();
                            updateStatus();
                        }
                    );


                    const size =
                        document.createElement(
                            "span"
                        );

                    size.className =
                        "upload-preview-size";

                    size.textContent =
                        formatBytes(
                            file.size
                        );


                    wrapper.appendChild(
                        image
                    );

                    wrapper.appendChild(
                        remove
                    );

                    wrapper.appendChild(
                        size
                    );

                    preview.appendChild(
                        wrapper
                    );
                }
            );
        }


        async function addFiles(
            fileList
        ) {
            const files =
                Array.from(
                    fileList
                ).filter(
                    file =>
                        file.type.startsWith(
                            "image/"
                        )
                );

            if (files.length === 0) {
                return;
            }

            processingCount += 1;

            updateStatus();

            try {
                for (const file of files) {
                    try {
                        const compressed =
                            await compressImage(
                                file
                            );

                        selectedFiles.push(
                            compressed
                        );

                        renderPreview();
                    } catch (error) {
                        console.error(error);

                        alert(
                            (i18n.oneFailed || "One of the images could not be processed.")
                        );
                    }
                }
            } finally {
                processingCount -= 1;

                updateStatus();
            }
        }


        cameraInput.addEventListener(
            "change",
            async () => {
                const files =
                    Array.from(
                        cameraInput.files
                    );

                cameraInput.value = "";

                await addFiles(files);
            }
        );


        galleryInput.addEventListener(
            "change",
            async () => {
                const files =
                    Array.from(
                        galleryInput.files
                    );

                galleryInput.value = "";

                await addFiles(files);
            }
        );


        form.addEventListener(
            "submit",
            event => {
                if (processingCount > 0) {
                    event.preventDefault();

                    alert(
                        (i18n.stillProcessing || "Image processing is still in progress.")
                    );
                }
            }
        );


        form.addEventListener(
            "formdata",
            event => {
                event.formData.delete(
                    "images"
                );

                selectedFiles.forEach(
                    file => {
                        event.formData.append(
                            "images",
                            file,
                            file.name
                        );
                    }
                );
            }
        );
    }
);
