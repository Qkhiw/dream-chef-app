// frontend/src/App.jsx (เวอร์ชันแยกการทำงาน)
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [ingredients, setIngredients] = useState('');
  const [quantity, setQuantity] = useState('');
  const [style, setStyle] = useState('อาหารสตรีทฟู้ดเยาวราช');
  
  const [isImageLoading, setIsImageLoading] = useState(false);
  const [isRecipeLoading, setIsRecipeLoading] = useState(false);
  const [error, setError] = useState(null);

  const [imageUrl, setImageUrl] = useState('');
  const [recipe, setRecipe] = useState(null);

  // --- ฟังก์ชันที่ 1: สำหรับสร้างภาพ ---
  const handleGenerateImage = async (event) => {
    event.preventDefault();
    if (!ingredients) {
      alert('กรุณากรอกข้อมูลวัตถุดิบ');
      return;
    }
    setRecipe(null); setImageUrl(''); setError(null);
    setIsImageLoading(true);
    try {
      const response = await fetch('/api/generate-image', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients, quantity, style }),
      });
      if (!response.ok) throw new Error((await response.json()).error || 'ไม่สามารถสร้างภาพได้');
      const data = await response.json();
      setImageUrl(data.image_url);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsImageLoading(false);
    }
  };

  // --- ฟังก์ชันที่ 2: สำหรับสร้างสูตรอาหาร ---
  const handleGenerateRecipe = async () => {
    setIsRecipeLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/generate-recipe', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients, quantity, style }),
      });
      if (!response.ok) throw new Error((await response.json()).instructions || 'ไม่สามารถสร้างสูตรได้');
      const data = await response.json();
      setRecipe(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRecipeLoading(false);
    }
  };

  // --- ส่วน Save และ Warning (เหมือนเดิม) ---
  const handleSaveImage = () => { /* โค้ดเดิม */ if (!imageUrl) return; const link = document.createElement('a'); link.href = imageUrl; const fileName = recipe?.menu_name ? `${recipe.menu_name}.png` : 'dream-chef-image.png'; link.download = fileName; document.body.appendChild(link); link.click(); document.body.removeChild(link); };
  const handleSaveRecipe = () => { /* โค้ดเดิม */ if (!recipe) return; const recipeText = `เมนู: ${recipe.menu_name}\n\nวิธีทำ:\n${recipe.instructions}`; const blob = new Blob([recipeText], { type: 'text/plain;charset=utf-8' }); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = `${recipe.menu_name}.txt`; document.body.appendChild(link); link.click(); document.body.removeChild(link); URL.revokeObjectURL(url); };
  useEffect(() => { const handleBeforeUnload = (event) => { if (imageUrl) { event.preventDefault(); event.returnValue = ''; } }; window.addEventListener('beforeunload', handleBeforeUnload); return () => window.removeEventListener('beforeunload', handleBeforeUnload); }, [imageUrl]);

  return (
    <div className="app-container">
      <div className="main-card">
        {/* ... ส่วนฟอร์ม ... */}
        <form onSubmit={handleGenerateImage}>
            <h1 className="title">นักปรุงฝัน</h1>
            <p className="subtitle">บอกวัตถุดิบ แล้วให้ AI ปรุงฝันให้คุณ</p>
            <div className="form-group"><label htmlFor="ingredients-input">วัตถุดิบของคุณ:</label><input id="ingredients-input" type="text" value={ingredients} onChange={(e) => setIngredients(e.target.value)} placeholder="เช่น เนื้อแกะ, โรสแมรี่, แสงจันทร์..."/></div>
            <div className="form-group"><label htmlFor="quantity-input">จำนวน/ปริมาณ:</label><input id="quantity-input" type="text" value={quantity} onChange={(e) => setQuantity(e.target.value)} placeholder="เช่น 2 ชิ้น, 1 กิโลกรัม, 1 ขวด..."/></div>
            <div className="form-group"><label htmlFor="style-select">เลือกสไตล์การปรุง:</label><select id="style-select" value={style} onChange={(e) => setStyle(e.target.value)}><option value="Thai Street Food in Yaowarat at night">อาหารสตรีทฟู้ดเยาวราช</option><option value="Royal Thai Cuisine served in golden plate">อาหารชาววังเครื่องทอง</option><option value="Spicy Isaan style with sticky rice">อาหารอีสานรสแซ่บ</option><option value="Floating market food on a boat">อาหารในตลาดน้ำ</option><option value="Southern Thai food, very spicy and colorful">อาหารใต้รสจัดจ้าน</option><option value="Modern Thai cuisine, fine dining presentation">อาหารไทยสไตล์โมเดิร์น</option></select></div>
            <button type="submit" disabled={isImageLoading || isRecipeLoading}>{isImageLoading ? 'กำลังวาดภาพ...' : 'เสกสรรปั้นแต่ง!'}</button>
        </form>
      </div>
      <div className="result-section">
        <div className={`cauldron-container ${isImageLoading ? 'loading' : ''}`}>
          {isImageLoading && <div className="loader"></div>}
          {error && !isImageLoading && <div className="error-message">{error}</div>}
          {!imageUrl && !isImageLoading && !error && (<div className="placeholder"><span>🍲</span><p>ผลงานของคุณจะปรากฏที่นี่</p></div>)}
          {imageUrl && (<img src={imageUrl} alt="Generated food" className="result-image-display" />)}
        </div>
        
        {/* --- ปุ่มและส่วนแสดงผลใหม่ --- */}
        {imageUrl && !recipe && !isRecipeLoading && (
            <button onClick={handleGenerateRecipe} className="generate-recipe-btn">📖 สร้างสูตรอาหารสำหรับภาพนี้</button>
        )}
        {isRecipeLoading && <div className="loader-small">กำลังคิดสูตร...</div>}
        {recipe && (
          <div className="recipe-card">
            <h2>{recipe.menu_name}</h2>
            <p>{recipe.instructions}</p>
            <div className="save-buttons-container">
              <button onClick={handleSaveImage} className="save-button">🖼️ บันทึกรูปภาพ</button>
              <button onClick={handleSaveRecipe} className="save-button">📝 บันทึกสูตร</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;