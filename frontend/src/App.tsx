import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const API_URL = process.env.REACT_APP_API_URL || '';
  const [items, setItems] = useState<{id: number, name: string, instance_id: string, use_cache: string}[]>([]);
  const [loading, setLoading] = useState(true);
  const [newItemName, setNewItemName] = useState<string>('');

  const fetchItems = async () => {
    try {
      const res = await fetch(`${API_URL}/items`);
      if (!res.ok) throw new Error('Failed to fetch items');
      const data = await res.json();
      setItems(data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemName.trim()) return;

    try {
      await fetch(`${API_URL}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newItemName })
      });
      setNewItemName('');
      fetchItems();
    } catch (err) {
      console.error('Ошибка при создании:', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await fetch(`${API_URL}/items/${id}`, {
        method: 'DELETE',
      });
      fetchItems();
    } catch (err) {
      console.error('Ошибка при удалении:', err);
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="App">
      <h1>Список товаров</h1>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={newItemName}
          onChange={(e) => setNewItemName(e.target.value)}
          placeholder="Название нового товара"
        />
        <button type="submit">Добавить</button>
      </form>
      
      <ul>
        {items.map(item => (
          <li key={item.id} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #ccc' }}>
            {/* Отображаем все три поля */}
            <strong>Товар:</strong> {item.name} <br />
            <div style={{ color: '#666' }}>
              <strong>Используется кеш:</strong> {item.use_cache}
            </div>
            <div style={{ color: '#666' }}>
              <strong>Ответ от инстанса:</strong> {item.instance_id}
            </div>
            <button 
              onClick={() => handleDelete(item.id)}
              style={{ marginLeft: '10px', color: 'red', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              Удалить
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
export default App;