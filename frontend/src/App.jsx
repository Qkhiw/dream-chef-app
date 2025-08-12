// frontend/src/App.jsx (เวอร์ชันมีฟังก์ชัน Save)
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  // --- State Management (เหมือนเดิม) ---
  const [ingredients, setIngredients] = useState('');
  const [quantity, setQuantity] = useState('');
  const [style, setStyle] = useState('อาหารสตรีทฟู้ดเยาวราช');
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [imageUrl, setImageUrl] = useState('');
  const [recipe, setRecipe] = useState(null);

  // --- ฟังก์ชันใหม่: สำหรับบันทึกรูปภาพ ---
  const handleSaveImage = () => {
    if (!imageUrl) return;
    // สร้าง Link ชั่วคราวเพื่อดาวน์โหลด
    const link = document.createElement('a');
    link.href = imageUrl;
    // ตั้งชื่อไฟล์จากชื่อเมนู หรือถ้าไม่มีก็ใช้ชื่อ default
    const fileName = recipe?.menu_name ? `${recipe.menu_name}.png` : 'dream-chef-image.png';
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // --- ฟังก์ชันใหม่: สำหรับบันทึกสูตรอาหาร ---
  const handleSaveRecipe = () => {
    if (!recipe) return;
    const recipeText = `เมนู: ${recipe.menu_name}\n\nวิธีทำ:\n${recipe.instructions}`;
    const blob = new Blob([recipeText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${recipe.menu_name}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // --- ฟังก์ชันสำหรับ Submit (เหมือนเดิม) ---
  const handleSubmit = async (event) => {
    // ... (โค้ดใน handleSubmit เหมือนเดิมทุกประการ) ...
    event.preventDefault();
    if (!ingredients || !quantity) {
      alert('กรุณากรอกข้อมูลวัตถุดิบและจำนวนให้ครบถ้วน');
      return;
    }
    setImageUrl(''); setRecipe(null); setError(null);
    setIsLoading(true);
    try {
      const response = await fetch('/api/generate-creation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients, quantity, style }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'มีบางอย่างผิดพลาด');
      }
      const data = await response.json();
      setImageUrl(data.image_url);
      setRecipe(JSON.parse(data.recipe));
    } catch (err) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Effect ใหม่: สำหรับแสดงคำเตือนก่อนออกจากหน้า ---
  useEffect(() => {
    const handleBeforeUnload = (event) => {
      // แสดงคำเตือนก็ต่อเมื่อมีผลลัพธ์แสดงอยู่
      if (imageUrl && recipe) {
        event.preventDefault();
        event.returnValue = ''; // ข้อความมาตรฐานของเบราว์เซอร์จะแสดงขึ้นมา
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup function: จะทำงานเมื่อ component ถูกทำลายเพื่อลบ event listener ออก
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [imageUrl, recipe]); // Effect นี้จะทำงานเมื่อ imageUrl หรือ recipe เปลี่ยนแปลง


  // --- JSX Rendering ---
  return (
    <div className="app-container">
      {/* ... ส่วน main-card และ form เหมือนเดิม ... */}
      <div className="main-card">
        <h1 className="title">นักปรุงฝัน</h1>
        <p className="subtitle">บอกวัตถุดิบ แล้วให้ AI ปรุงฝันให้คุณ</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group"><label htmlFor="ingredients-input">วัตถุดิบของคุณ:</label><input id="ingredients-input" type="text" value={ingredients} onChange={(e) => setIngredients(e.target.value)} placeholder="เช่น เนื้อแกะ, โรสแมรี่, แสงจันทร์..."/></div>
          <div className="form-group"><label htmlFor="quantity-input">จำนวน/ปริมาณ:</label><input id="quantity-input" type="text" value={quantity} onChange={(e) => setQuantity(e.target.value)} placeholder="เช่น 2 ชิ้น, 1 กิโลกรัม, 1 ขวด..."/></div>
          <div className="form-group"><label htmlFor="style-select">เลือกสไตล์การปรุง:</label><select id="style-select" value={style} onChange={(e) => setStyle(e.target.value)}><option value="Thai Street Food in Yaowarat at night">อาหารสตรีทฟู้ดเยาวราช</option><option value="Royal Thai Cuisine served in golden plate">อาหารชาววังเครื่องทอง</option><option value="Spicy Isaan style with sticky rice">อาหารอีสานรสแซ่บ</option><option value="Floating market food on a boat">อาหารในตลาดน้ำ</option><option value="Southern Thai food, very spicy and colorful">อาหารใต้รสจัดจ้าน</option><option value="Modern Thai cuisine, fine dining presentation">อาหารไทยสไตล์โมเดิร์น</option></select></div>
          <button type="submit" disabled={isLoading}>{isLoading ? 'กำลังปรุง...' : 'เสกสรรปั้นแต่ง!'}</button>
        </form>
      </div>
      
      <div className="result-section">
        {/* ... cauldron-container เหมือนเดิม ... */}
        <div className={`cauldron-container ${isLoading ? 'loading' : ''}`}>
          {isLoading && <div className="loader"></div>}
          {!isLoading && error && <div className="error-message">เกิดข้อผิดพลาด: <br/> {error}</div>}
          {!isLoading && !error && !imageUrl && (<div className="placeholder"><span>🍲</span><p>ผลงานของคุณจะปรากฏที่นี่</p></div>)}
          {!isLoading && imageUrl && (<img src={imageUrl} alt="Generated food" className="result-image-display" />)}
        </div>
        
        {/* --- ส่วนที่แก้ไข: เพิ่มปุ่ม Save --- */}
        {!isLoading && recipe && (
          <div className="recipe-card">
            <h2>{recipe.menu_name || "ชื่อเมนู"}</h2>
            <p>{recipe.instructions || "วิธีทำ"}</p>
            {/* --- Container สำหรับปุ่ม Save --- */}
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