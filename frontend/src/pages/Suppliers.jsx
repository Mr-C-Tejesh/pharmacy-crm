import React, { useState, useEffect, useCallback } from "react";
import { api } from "../api";
import { Spinner, Modal, Field } from "../components";

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({});
  const [error, setError] = useState("");

  const fetchSuppliers = useCallback(() => {
    setLoading(true);
    api.suppliers.list()
      .then(res => setSuppliers(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchSuppliers();
  }, [fetchSuppliers]);

  const handleSave = async () => {
    try {
      setError("");
      await api.suppliers.create(formData);
      setShowModal(false);
      fetchSuppliers();
    } catch (e) {
      setError(e.message);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Suppliers</h1>
          <p className="page-sub">Manage your pharmaceutical suppliers</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => { setFormData({}); setShowModal(true); }}>
            + Add Supplier
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Contact Person</th>
                <th>Phone</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map(s => (
                <tr key={s.id} className="table-row">
                  <td className="td-mono">#{s.id}</td>
                  <td className="td-primary">{s.name}</td>
                  <td>{s.contact_person || "—"}</td>
                  <td>{s.phone || "—"}</td>
                  <td>{s.email || "—"}</td>
                </tr>
              ))}
              {suppliers.length === 0 && (
                <tr>
                  <td colSpan="5" className="empty-cell">No suppliers found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <Modal
          title="Add New Supplier"
          onClose={() => setShowModal(false)}
          footer={
            <>
              {error && <span className="modal-err">{error}</span>}
              <button className="btn btn-primary" onClick={handleSave}>Save Supplier</button>
            </>
          }
        >
          <Field label="Supplier Name">
            <input className="input" value={formData.name || ""} onChange={e => setFormData({ ...formData, name: e.target.value })} />
          </Field>
          <Field label="Contact Person">
            <input className="input" value={formData.contact_person || ""} onChange={e => setFormData({ ...formData, contact_person: e.target.value })} />
          </Field>
          <Field label="Phone">
            <input className="input" value={formData.phone || ""} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
          </Field>
          <Field label="Email">
            <input className="input" type="email" value={formData.email || ""} onChange={e => setFormData({ ...formData, email: e.target.value })} />
          </Field>
          <Field label="Address" full>
            <input className="input" value={formData.address || ""} onChange={e => setFormData({ ...formData, address: e.target.value })} />
          </Field>
        </Modal>
      )}
    </div>
  );
}
