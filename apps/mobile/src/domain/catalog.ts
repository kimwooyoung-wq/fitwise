export type CatalogItem = {
  product_id: string;
  brand_name: string;
  product_name: string;
  category_code: string;
  product_url: string;
  product_observed_at: string;
  product_expires_at: string;
  seller_name: string;
  price_minor: number;
  currency_code: string;
  stock_status: 'in_stock' | 'low_stock';
  purchase_url: string;
  offer_observed_at: string;
  offer_expires_at: string;
};

export type CatalogSearchResponse = {
  query: string | null;
  category: string | null;
  budget_max: number;
  items: CatalogItem[];
  data_notice: string;
};
