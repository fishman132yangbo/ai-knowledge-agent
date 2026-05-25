export type UploadDocumentResponse = {
  filename: string;
  content_type?: string;
  path?: string;
};

export async function uploadDocument(file: File): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/documents/upload", {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error(`上传失败：${response.status}`);
  }

  return response.json() as Promise<UploadDocumentResponse>;
}
