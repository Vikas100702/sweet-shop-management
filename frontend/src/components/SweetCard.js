/**
 * Sweet Card Component
 * Displays individual sweet product with purchase functionality
 */
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { showSuccess, showError } from './Toast';

const SweetCard = ({ sweet, onUpdate, onEdit }) => {
  const { isAdmin } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [purchaseQuantity, setPurchaseQuantity] = useState(1);
  const [showQuantitySelector, setShowQuantitySelector] = useState(false);

  // Calculate stock status
  const isOutOfStock = sweet.quantity === 0;
  const isLowStock = sweet.quantity > 0 && sweet.quantity <= 10;

  /**
   * Handle sweet purchase
   */
  const handlePurchase = async () => {
    if (purchaseQuantity <= 0 || purchaseQuantity > sweet.quantity) {
      showError('Invalid quantity selected');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiService.purchaseSweet(sweet.id, { 
        quantity: purchaseQuantity 
      });
      
      showSuccess(
        `Purchased ${purchaseQuantity} ${sweet.name}(s) for ${response.total_cost.toFixed(2)}`
      );
      
      // Reset purchase form
      setShowQuantitySelector(false);
      setPurchaseQuantity(1);
      
      // Refresh sweet data
      if (onUpdate) onUpdate();
    } catch (error) {
      showError(apiService.getErrorMessage(error));
    } finally {
      setIsLoading(false); // ✅ properly closed
    }
  };

  return (
    <div className="sweet-card">
      <h3>{sweet.name}</h3>
      <p>Category: {sweet.category}</p>
      <p>Price: ${sweet.price.toFixed(2)}</p>
      <p>Quantity: {sweet.quantity}</p>

      {isOutOfStock ? (
        <span className="out-of-stock">Out of stock</span>
      ) : (
        <>
          {showQuantitySelector ? (
            <div>
              <input
                type="number"
                min="1"
                max={sweet.quantity}
                value={purchaseQuantity}
                onChange={(e) => setPurchaseQuantity(Number(e.target.value))}
                disabled={isLoading}
              />
              <button onClick={handlePurchase} disabled={isLoading}>
                {isLoading ? 'Processing...' : 'Confirm Purchase'}
              </button>
              <button onClick={() => setShowQuantitySelector(false)} disabled={isLoading}>
                Cancel
              </button>
            </div>
          ) : (
            <button 
              onClick={() => setShowQuantitySelector(true)} 
              disabled={isLoading || isOutOfStock}
            >
              Buy
            </button>
          )}
        </>
      )}

      {isAdmin && (
        <button onClick={() => onEdit && onEdit(sweet)}>Edit</button>
      )}

      {isLowStock && <span className="low-stock">Low stock!</span>}
    </div>
  );
};

export default SweetCard;
