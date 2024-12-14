
export class FileSystemAPI {
  constructor(baseURL = "") {
    this.baseURL = baseURL;
  }

  async readFile(filename, prefix="", binary = false) {
    const response = await fetch(`${this.baseURL}/${prefix}${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to read file: ${response.statusText}`);
    }
    if (binary) {
      return response.arrayBuffer();
    } else {
      return response.text();
    }
  }

  async writeFile(filename, data) {
    const response = await fetch(`${this.baseURL}/.file/${filename}`, {
      method: "POST",
      body: data,
      headers: {
        "Content-Type":
          typeof data === "string" ? "text/plain" : "application/octet-stream",
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to write file: ${response.statusText}`);
    }
    return response.text();
  }

  async listFiles() {
    const response = await fetch(`${this.baseURL}/.files`);
    if (!response.ok) {
      throw new Error(`Failed to list files: ${response.statusText}`);
    }
    return response.json();
  }

  async deleteFile(filename) {
    const response = await fetch(`${this.baseURL}/.file/${filename}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error(`Failed to delete file: ${response.statusText}`);
    }
    return response.text();
  }
}
