const BASE = process.env.REACT_APP_API_URL || "https://pharmacy-crm-api.onrender.com";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const msg =
      typeof err.detail === "object"
        ? err.detail.error || JSON.stringify(err.detail)
        : err.detail || "Request failed";
    throw new Error(msg);
  }

  return res.json();
}

export const api = {
  dashboard: {
    summary:        () => request("/dashboard/summary"),
    lowStock:       () => request("/dashboard/low-stock"),
    recentSales:    () => request("/dashboard/recent-sales"),
    purchaseOrders: () => request("/dashboard/purchase-orders"),
  },
  inventory: {
    overview: () => request("/inventory/overview"),
    list: ({ search = "", status = "", page = 1, limit = 10 } = {}) => {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (status) params.append("status", status);
      params.append("page",  page);
      params.append("limit", limit);
      return request(`/inventory/?${params.toString()}`);
    },
    get:    (id)       => request(`/inventory/${id}`),
    create: (data)     => request("/inventory/", { method: "POST", body: JSON.stringify(data) }),
    update: (id, data) => request(`/inventory/${id}`, { method: "PUT",   body: JSON.stringify(data) }),
    updateStatus: (id, status) =>
      request(`/inventory/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  },
  billing: {
    list: ({ page = 1, limit = 10 } = {}) => request(`/billing/?page=${page}&limit=${limit}`),
    createSale: (data) => request("/billing/", { method: "POST", body: JSON.stringify(data) }),
  },
  suppliers: {
    list: ({ search = "", page = 1, limit = 10 } = {}) => {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      params.append("page", page);
      params.append("limit", limit);
      return request(`/suppliers/?${params.toString()}`);
    },
    create: (data) => request("/suppliers/", { method: "POST", body: JSON.stringify(data) }),
  }
};