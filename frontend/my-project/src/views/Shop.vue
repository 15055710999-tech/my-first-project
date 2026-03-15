<template>
  <div class="shop-container">
    <h1>篮球商城</h1>
    <p class="desc">
      购买篮球装备、课程等，与训练计划结合使用，打造一站式篮球学习体验。
    </p>

    <div class="products-grid">
      <div
        v-for="(product, index) in products"
        :key="index"
        class="product-card"
      >
        <div class="image" />
        <h2>{{ product.name }}</h2>
        <p class="category">{{ formatCategory(product.category) }}</p>
        <p class="price">￥{{ product.price }}</p>
        <p class="summary">{{ product.description }}</p>
        <button class="add-btn" @click="addToCart(product)">
          加入购物车
        </button>
      </div>
    </div>

    <div class="cart-card" v-if="cartItems.length > 0">
      <h2>购物车</h2>
      <ul class="cart-list">
        <li v-for="item in cartItems" :key="item.product_id" class="cart-item">
          <span>{{ item.name }}</span>
          <span>x{{ item.quantity }}</span>
        </li>
      </ul>
      <button class="submit-btn" @click="handleCreateOrder" :disabled="submitting">
        {{ submitting ? '提交订单中...' : '提交订单（示例）' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getProductsApi, createOrderApi } from '../api/basketball'

interface Product {
  id?: number
  name: string
  category: string
  description?: string
  price: string
}

interface CartItem {
  product_id: number
  name: string
  quantity: number
}

const products = ref<Product[]>([])
const cartItems = ref<CartItem[]>([])
const submitting = ref(false)

const fetchProducts = async () => {
  try {
    const res: any = await getProductsApi()
    products.value = res.data || []
  } catch (e) {
    console.error('获取商品失败', e)
  }
}

const formatCategory = (c: string) => {
  switch (c) {
    case 'gear':
      return '篮球装备'
    case 'course':
      return '训练课程'
    case 'apparel':
      return '篮球服饰'
    default:
      return '其他'
  }
}

const addToCart = (product: Product) => {
  if (!product.id) {
    alert('当前示例商品还没有真实 ID，创建商品后即可下单。')
    return
  }
  const found = cartItems.value.find((c) => c.product_id === product.id)
  if (found) {
    found.quantity += 1
  } else {
    cartItems.value.push({
      product_id: product.id,
      name: product.name,
      quantity: 1
    })
  }
}

const handleCreateOrder = async () => {
  if (!cartItems.value.length) return
  submitting.value = true
  try {
    await createOrderApi({
      items: cartItems.value.map((c) => ({
        product_id: c.product_id,
        quantity: c.quantity
      }))
    })
    alert('订单创建成功（示例），后续可接入支付等流程。')
    cartItems.value = []
  } catch (e) {
    console.error('创建订单失败', e)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.shop-container {
  padding: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

h1 {
  font-size: 26px;
  color: #333;
  margin-bottom: 8px;
}

.desc {
  color: #666;
  margin-bottom: 18px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.product-card {
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.image {
  width: 100%;
  height: 120px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-bottom: 8px;
}

.product-card h2 {
  font-size: 16px;
  margin-bottom: 4px;
}

.category {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.price {
  color: #e53935;
  font-weight: bold;
  margin-bottom: 4px;
}

.summary {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.add-btn {
  padding: 6px 12px;
  border-radius: 16px;
  border: none;
  background: #667eea;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
}

.cart-card {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.cart-list {
  list-style: none;
  margin-bottom: 10px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.submit-btn {
  padding: 8px 20px;
  border-radius: 18px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

