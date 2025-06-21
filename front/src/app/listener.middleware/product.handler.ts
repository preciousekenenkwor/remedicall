import { isFulfilled, isRejectedWithValue, Middleware } from '@reduxjs/toolkit';
import { productApi } from '../services/products/productApi';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const productHandler: Middleware = (_storeAPI) => (next) => (action) => {
  if (productApi.endpoints.fetchProducts.matchPending(action)) {
    console.log('Fetching products...');
  }
  if (productApi.endpoints.fetchProductById.matchPending(action)) {
    console.log(`Fetching product with ID: ${action.meta.arg}`);
  }

  if (isFulfilled(action)) {
    console.log('API call succeeded:', action);
  }

  if (isRejectedWithValue(action)) {
    console.error('API call failed:', action);
  }

  return next(action);
};

export default productHandler;
