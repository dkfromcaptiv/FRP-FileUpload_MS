document.getElementById("view-all-button").addEventListener("click", function () {
  const myHeaders = new Headers();
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

  fetch("https://646zta6xqd.execute-api.ap-south-1.amazonaws.com/Fetch", requestOptions)
    .then((response) => response.json())
    .then((result) => {
      populateFileSections(result['file-section-header']);
    })
    .catch((error) => console.error('Error:', error));
});


let base64Content = "";
let fileExtension = "";

function populateFileSections(fileSectionsData) {
  Object.keys(fileSectionsData).forEach(section => {
    const fileList = document.getElementById(`${section}-files-list`);

    fileList.style.display = "grid";
    fileList.innerHTML = "";

    fileSectionsData[section].forEach(fileName => {
      const fileItem = document.createElement("div");
      fileItem.classList.add("file-item");

      const fileNameElement = document.createElement("span");
      fileNameElement.classList.add("file-name");
      fileNameElement.textContent = fileName;

      const buttonContainer = document.createElement("div");
      buttonContainer.classList.add("button-container");

      const viewBtn = document.createElement("button");
      viewBtn.classList.add("view-btn");
      viewBtn.textContent = "View";
      // Pass the file name and section heading dynamically to fetchData
      viewBtn.onclick = () => fetchData(fileName, section);

      const deleteBtn = document.createElement("button");
      deleteBtn.classList.add("delete-btn");
      deleteBtn.textContent = "Delete";
      deleteBtn.onclick = () => deleteFile(fileItem);

      buttonContainer.appendChild(viewBtn);
      buttonContainer.appendChild(deleteBtn);
      fileItem.appendChild(fileNameElement);
      fileItem.appendChild(buttonContainer);

      fileList.appendChild(fileItem);
    });
  });
}

function deleteFile(fileItem) {
  fileItem.remove();
}

function fetchData(fileName, heading) {
  const myHeaders = new Headers();
  myHeaders.append("authorization", "BBF091C2-9FBC-46CE-951C-AC797CA0AF78");

  const raw = JSON.stringify({
    filename: fileName,  // Use the dynamic filename
    meta: heading        // Use the dynamic heading
  });

  const requestOptions = {
    method: "POST",
    headers: myHeaders,
    body: raw,
    redirect: "follow"
  };

  fetch("https://646zta6xqd.execute-api.ap-south-1.amazonaws.com/download", requestOptions)
    .then((response) => response.json())
    .then((result) => {
      base64Content = result.base64_content;
      fileExtension = result.file_extension;
      viewFile(fileName);
    })
    .catch((error) => {
      console.error('Error:', error);
      document.getElementById('result').textContent = 'Error fetching data.';
    });
}

function viewFile(fileName) {
  if (!base64Content || !fileExtension) {
    document.getElementById('result').textContent = 'Please fetch data first.';
    return;
  }

  const popup = document.createElement("div");
  popup.style.position = "fixed";
  popup.style.top = "50%";
  popup.style.left = "50%";
  popup.style.transform = "translate(-50%, -50%)";
  popup.style.backgroundColor = "#fff";
  popup.style.padding = "30px";
  popup.style.boxShadow = "0 0 10px rgba(0, 0, 0, 0.1)";
  popup.style.zIndex = "9999";
  popup.style.maxWidth = "400px";
  popup.style.width = "100%";
  popup.style.textAlign = "center";

  const img = document.createElement("img");
  img.src = `data:image/${fileExtension};base64,${base64Content}`;
  img.style.width = "100%"; // Resize image as needed
  img.style.height = "auto";

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "X";
  closeBtn.style.position = "absolute";
  closeBtn.style.top = "5px";
  closeBtn.style.right = "5px";
  closeBtn.style.backgroundColor = "transparent";
  closeBtn.style.border = "none";
  closeBtn.style.fontSize = "20px";
  closeBtn.style.cursor = "pointer";
  closeBtn.onclick = () => {
    popup.remove();
  };

  const downloadBtn = document.createElement("button");
  downloadBtn.textContent = "Download";
  downloadBtn.style.marginTop = "20px";
  downloadBtn.style.backgroundColor = "#007bff";
  downloadBtn.style.color = "white";
  downloadBtn.style.padding = "10px 20px";
  downloadBtn.style.border = "none";
  downloadBtn.style.cursor = "pointer";
  downloadBtn.onclick = () => {
    const link = document.createElement("a");
    link.href = img.src;
    link.download = fileName; // Set the file name for download
    link.click();
  };

  popup.appendChild(closeBtn);
  popup.appendChild(img);
  popup.appendChild(downloadBtn);

  document.body.appendChild(popup);
}
