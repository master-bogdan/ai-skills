type DownloadFileInput = {
  filename: string;
  content: string;
  mimeType: string;
};

export const downloadFile = ({ filename, content, mimeType }: DownloadFileInput): void => {
  const url = URL.createObjectURL(new Blob([content], { type: mimeType }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};
