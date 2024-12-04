let token = "";

function triggerFileUpload() {
    const documentType = document.getElementById("document-type").value;
    if (documentType === "select") {
        alert("Please select a document type.");
    } else {
        document.getElementById("fileInput").click();
    }
}

function verify() {
    const myHeaders = new Headers();
    myHeaders.append("Authorization", "BBF091C2-9FBC-46CE-951C-AC797CA0AF78");
    myHeaders.append("Content-Type", "application/json");

    const raw = JSON.stringify({
        "tenant_id": "DA9909F1-AB16-4F53-8AAA-800B19A8BEE6"
    });

    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: raw,
        redirect: "follow"
    };

    fetch("https://646zta6xqd.execute-api.ap-south-1.amazonaws.com/Authenticate", requestOptions)
        .then(response => response.json())  
        .then(result => {           
            if (result.tenant_id && result.token) {
                token = result.token;  
                alert(`You have the permission to upload files for the user \n ${result.tenant_id}.`);
            } else {
                alert("Verification failed. Missing tenant_id or token.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Verification failed. Please try again.");
        });
}

document.getElementById("fileInput").addEventListener("change", async (event) => {
    const fileInput = document.getElementById("fileInput");
    if (fileInput.files.length === 0) {
        alert("Please select a file to upload.");
        return;
    }

    if (!token) {
        alert("Please verify the user first By clicking the 'verify' button in Top-Left.");
        return;
    }

    const files = fileInput.files;
    const documentType = document.getElementById("document-type").value;

    if (documentType === "select") {
        alert("Please select a document type before uploading.");
        return;
    }

    const leftSection = document.querySelector(".left-section");

    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = async () => {
            const fileContentBase64 = btoa(reader.result);
            const fileName = file.name;

            const myHeaders = new Headers();
            myHeaders.append("Authorization", "BBF091C2-9FBC-46CE-951C-AC797CA0AF78");
            myHeaders.append("Token", token);
            myHeaders.append("Content-Type", "application/json");

            const raw = JSON.stringify({
                metatag: documentType,
                fileContent: fileContentBase64,
                filename: fileName
            });

            const requestOptions = {
                method: "POST",
                headers: myHeaders,
                body: raw,
                redirect: "follow"
            };

            const progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");

            const progressBar = document.createElement("div");
            progressBar.classList.add("progress-bar");
            progressContainer.appendChild(progressBar);

            const uploadMessage = document.createElement("div");
            uploadMessage.classList.add("upload-message");
            uploadMessage.textContent = `Uploading file ${fileName}...`;

            leftSection.appendChild(progressContainer);
            leftSection.appendChild(uploadMessage);

            try {
                const response = await fetch("https://646zta6xqd.execute-api.ap-south-1.amazonaws.com/Upload", requestOptions);
                if (response.ok) {
                    uploadMessage.textContent = `File ${fileName} uploaded to ${documentType} successfully!`;
                    progressBar.style.width = "100%";
                    setTimeout(() => location.reload(), 2000); // Refresh the page after 2 seconds
                } else {
                    alert("Failed to upload file. Please try again.");
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert("Failed to upload file. Please try again.");
            }
        };

        reader.onerror = () => {
            alert("Could not read file. Please try again.");
        };

        reader.readAsBinaryString(file);
    });
});
