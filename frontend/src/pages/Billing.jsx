import React, { useState, useEffect } from "react";
import { api } from "../api";
import { Spinner, Modal, Field, StatusBadge } from "../components";

export default function Billing() {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [medicines, setMedicines] = useState([]);
  const [error, setError] = useState("");

  const [form, setForm] = useState({ patient_name: "", payment_mode: "Cash", items: [] });
  const [search, setSearch] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  const fetchSales = () => {
    setLoading(true);
    api.billing.list()
      .then(res => setSales(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const fetchMeds = () => {
    api.inventory.list({ limit: 100 }).then(res => setMedicines(res.data || []));
  };

  useEffect(() => {
    fetchSales();
    fetchMeds();
  }, []);

  const addItem = (med) => {
    setForm(prev => {
      const exists = prev.items.find(i => i.medicine_id === med.id);
      if (exists) {
        return {
          ...prev,
          items: prev.items.map(i => i.medicine_id === med.id ? { ...i, quantity: i.quantity + 1 } : i)
        };
      }
      return {
        ...prev,
        items: [...prev.items, { medicine_id: med.id, name: med.name, price: med.price, quantity: 1, stock: med.quantity }]
      };
    });
  };

  const updateItemQty = (id, delta) => {
    setForm(prev => ({
      ...prev,
      items: prev.items.map(i => i.medicine_id === id ? { ...i, quantity: Math.max(1, i.quantity + delta) } : i)
    }));
  };

  const removeItem = (id) => {
    setForm(prev => ({
      ...prev,
      items: prev.items.filter(i => i.medicine_id !== id)
    }));
  };

  const handleSave = async () => {
    if (!form.patient_name || form.items.length === 0) {
      setError("Please add patient name and at least one item.");
      return;
    }
    try {
      setError("");
      setSubmitting(true);
      
      const payload = {
        patient_name: form.patient_name,
        payment_mode: form.payment_mode,
        items: form.items.map(i => ({
          medicine_id: i.medicine_id,
          quantity: i.quantity
        }))
      };

      await api.billing.createSale(payload);
      
      setSuccess("Bill generated successfully!");
      setTimeout(() => setSuccess(""), 3000);
      
      setShowModal(false);
      setForm({ patient_name: "", payment_mode: "Cash", items: [] });
      fetchSales();
      fetchMeds();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const total = form.items.reduce((acc, item) => acc + (item.price * item.quantity), 0);

  if (loading) return <Spinner />;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Billing & Sales</h1>
          <p className="page-sub">Create invoices and view sales history</p>
        </div>
        <div className="header-actions">
          {success && <span className="stat-tag tag-green" style={{ alignSelf: 'center', marginRight: 12 }}>{success}</span>}
          <button className="btn btn-primary" onClick={() => { setForm({ patient_name: "", payment_mode: "Cash", items: [] }); setError(""); setShowModal(true); }}>
            + Create Invoice
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Invoice No</th>
                <th>Patient Name</th>
                <th>Date</th>
                <th>Items</th>
                <th>Payment</th>
                <th>Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {sales.map(s => (
                <tr key={s.id} className="table-row">
                  <td className="td-mono td-primary">{s.invoice_no}</td>
                  <td>{s.patient_name}</td>
                  <td>{new Date(s.created_at).toLocaleDateString("en-IN", { day: '2-digit', month: 'short', year: 'numeric' })}</td>
                  <td>{s.item_count}</td>
                  <td>{s.payment_mode}</td>
                  <td className="td-mono font-bold">₹{s.total_amount.toLocaleString("en-IN")}</td>
                  <td><StatusBadge status={s.status} /></td>
                </tr>
              ))}
              {sales.length === 0 && (
                <tr>
                  <td colSpan="7" className="empty-cell">No sales found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <Modal
          title="Create New Invoice"
          onClose={() => setShowModal(false)}
          footer={
            <>
              {error && <span className="modal-err">{error}</span>}
              <button className="btn btn-primary" onClick={handleSave} disabled={submitting}>
                {submitting ? "Processing..." : "Generate Bill"}
              </button>
            </>
          }
        >
          <Field label="Patient Name">
            <input className="input" value={form.patient_name} onChange={e => setForm({ ...form, patient_name: e.target.value })} placeholder="Enter patient name..." />
          </Field>
          <Field label="Payment Mode">
            <select className="input select" value={form.payment_mode} onChange={e => setForm({ ...form, payment_mode: e.target.value })}>
              <option>Cash</option>
              <option>Card</option>
              <option>UPI</option>
            </select>
          </Field>

          <Field label="Add Medicines" full>
            <input className="input" placeholder="Search to add..." value={search} onChange={e => setSearch(e.target.value)} />
            {search && (
              <div style={{ maxHeight: 120, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 'var(--radius-xs)', marginTop: 4 }}>
                {medicines.filter(m => m.name.toLowerCase().includes(search.toLowerCase())).map(med => (
                  <div key={med.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', borderBottom: '1px solid var(--border)', cursor: 'pointer' }} onClick={() => { addItem(med); setSearch(""); }}>
                    <span>{med.name} <small style={{ color: 'var(--text-3)' }}>({med.quantity} in stock)</small></span>
                    <span>₹{med.price}</span>
                  </div>
                ))}
              </div>
            )}
          </Field>

          <div className="field-full" style={{ marginTop: 16 }}>
            <label className="field-label">Invoice Items</label>
            <div style={{ background: 'var(--surface-2)', borderRadius: 'var(--radius-xs)', padding: 12 }}>
              {form.items.length === 0 ? <p style={{ fontSize: 12, color: 'var(--text-3)', textAlign: 'center' }}>No items added.</p> : (
                <table style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse' }}>
                  <tbody>
                    {form.items.map(item => (
                      <tr key={item.medicine_id} style={{ borderBottom: '1px solid var(--border)' }}>
                        <td style={{ padding: 4 }}>{item.name}</td>
                        <td style={{ padding: 4, width: 80 }}>
                          <button className="btn-edit" style={{ padding: '0 4px', marginRight: 4 }} onClick={() => updateItemQty(item.medicine_id, -1)}>-</button>
                          {item.quantity}
                          <button className="btn-edit" style={{ padding: '0 4px', marginLeft: 4 }} onClick={() => updateItemQty(item.medicine_id, 1)} disabled={item.quantity >= item.stock}>+</button>
                        </td>
                        <td style={{ padding: 4, textAlign: 'right' }}>₹{item.price * item.quantity}</td>
                        <td style={{ padding: 4, width: 24 }}><button className="btn-ghost" onClick={() => removeItem(item.medicine_id)}>✕</button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <div style={{ textAlign: 'right', marginTop: 12, fontSize: 16, fontWeight: 800 }}>
              Total: ₹{total.toLocaleString("en-IN")}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
