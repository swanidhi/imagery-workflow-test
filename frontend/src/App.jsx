import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ProductDetail from './components/ProductDetail';
import ComparisonModal from './components/ComparisonModal';
import { Loader2 } from 'lucide-react';

function App() {
  const [products, setProducts] = useState([]);
  const [selectedCupid, setSelectedCupid] = useState(null);
  const [currentProductData, setCurrentProductData] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  // Comparison State
  const [compareModalOpen, setCompareModalOpen] = useState(false);

  const [srcListForCompare, setSrcListForCompare] = useState([]);
  const [srcIndexForCompare, setSrcIndexForCompare] = useState(0);

  const [aiListForCompare, setAiListForCompare] = useState([]);
  const [aiIndexForCompare, setAiIndexForCompare] = useState(0);

  useEffect(() => {
    fetchProducts();
  }, []);

  // Also refresh products when a generation happens
  const fetchProducts = async () => {
    try {
      // In dev mode we might need CORS or proxy. 
      // Assuming Flask serves this app or proxy is set up.
      // For now, hardcode localhost:8080 if running separately
      const res = await fetch('http://localhost:8080/api/products');
      const data = await res.json();
      setProducts(data.products);
      setLoading(false);
    } catch (e) {
      console.error("Failed to fetch products", e);
      setLoading(false);
    }
  };

  const handleSelectProduct = async (cupid) => {
    setSelectedCupid(cupid);
    // Fetch detail
    try {
      const res = await fetch(`http://localhost:8080/api/product/${cupid}`);
      const data = await res.json();
      setCurrentProductData(data);
    } catch (e) {
      console.error(e);
    }
  };

  // Accept activeSourceUrlList from the child component
  const handleGenerate = async (activeSourceUrlList) => {
    if (!selectedCupid) return;
    try {
      await fetch('http://localhost:8080/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cupid_name: selectedCupid,
          active_sources: activeSourceUrlList // Send as list
        })
      });
      // Refresh data
      handleSelectProduct(selectedCupid);
      fetchProducts();
    } catch (e) {
      alert("Generation failed");
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background text-text">
      <Sidebar
        products={products}
        selectedCupid={selectedCupid}
        onSelect={handleSelectProduct}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />

      <main className="flex-1 flex flex-col relative w-full overflow-hidden">
        {selectedCupid && currentProductData ? (
          <ProductDetail
            data={currentProductData}
            onGenerate={handleGenerate}
            onCompare={(srcIdx, aiIdx) => {
              setSrcListForCompare(currentProductData.ghost_images || []);
              setSrcIndexForCompare(srcIdx);

              setAiListForCompare(currentProductData.generated_images || []);
              setAiIndexForCompare(aiIdx);
              setCompareModalOpen(true);
            }}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center text-text-muted">
            {loading ? <Loader2 className="animate-spin" /> : "Select a product to begin"}
          </div>
        )}
      </main>

      {compareModalOpen && (
        <ComparisonModal
          sourceImages={srcListForCompare}
          initialSourceIndex={srcIndexForCompare}
          aiImages={aiListForCompare}
          initialAiIndex={aiIndexForCompare}
          onClose={() => setCompareModalOpen(false)}
        />
      )}
    </div>
  );
}

export default App;
