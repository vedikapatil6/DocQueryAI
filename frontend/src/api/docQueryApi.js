import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${BASE_URL}/upload_pdf/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then(res => res.data);
}

export async function queryDoc(docId, query) {
  const formData = new FormData();
  formData.append("doc_id", docId);
  formData.append("query", query);
  return axios.post(`${BASE_URL}/query_doc/`, formData).then(res => res.data);
}
