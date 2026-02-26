// src/app/products/page.tsx
import Image from "next/image";
import Link from "next/link";

type Product = {
  product_id: number;
  name: string;
  brand?: string | null;
  price?: number | null;
  image_url?: string | null;
};

type ProductListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: Product[];
};

async function getProducts(): Promise<ProductListResponse> {
  const res = await fetch("/api/v1/products?limit=20&offset=0", { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch products: ${res.status}`);
  return res.json();
}

export default async function ProductsPage() {
  const data = await getProducts();

  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 16 }}>Products</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 16 }}>
        {data.items.map((p) => (
          <Link
            key={p.product_id}
            href={`/products/${p.product_id}`}
            style={{
              display: "block",
              border: "1px solid #eee",
              borderRadius: 12,
              overflow: "hidden",
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div style={{ position: "relative", width: "100%", aspectRatio: "4 / 5", background: "#f5f5f5" }}>
              {p.image_url ? (
                <Image
                  src={p.image_url}
                  alt={p.name}
                  fill
                  style={{ objectFit: "cover" }}
                  sizes="(max-width: 768px) 50vw, 25vw"
                />
              ) : null}
            </div>

            <div style={{ padding: 12 }}>
              <div style={{ fontSize: 12, opacity: 0.6 }}>{p.brand ?? ""}</div>
              <div style={{ fontSize: 14, fontWeight: 600, marginTop: 6 }}>{p.name}</div>
              <div style={{ fontSize: 14, marginTop: 8 }}>
                {p.price != null ? `${p.price.toLocaleString()}원` : ""}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}