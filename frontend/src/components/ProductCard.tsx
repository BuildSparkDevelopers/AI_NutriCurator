"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { ShoppingCart } from "lucide-react";
import { Product } from "@/lib/types";
import { formatPrice } from "@/lib/mock-data";

interface ProductCardProps {
  product: Product;
  index?: number;
}

export default function ProductCard({ product, index = 0 }: ProductCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
    >
      <Link
        href={`/products/${product.product_id}`}
        className="group block"
      >
        <div className="relative aspect-[4/5] rounded-md overflow-hidden bg-gray-100 mb-3">
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            sizes="(max-width: 768px) 50vw, 25vw"
          />
          {product.discount_rate > 0 && (
            <span className="absolute top-2 left-2 bg-warn-red text-white text-xs font-bold px-2 py-1 rounded">
              {product.discount_rate}%
            </span>
          )}
          <button
            className="absolute bottom-2 right-2 w-9 h-9 bg-white rounded-full shadow-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-primary hover:text-white"
            onClick={(e) => {
              e.preventDefault();
            }}
          >
            <ShoppingCart size={16} />
          </button>
        </div>

        <div className="space-y-1">
          <p className="text-[11px] text-gray-400">{product.brand}</p>
          <h3 className="text-sm text-gray-600 leading-snug line-clamp-2 group-hover:text-primary transition-colors">
            {product.name}
          </h3>
          <div className="flex items-center gap-2">
            {product.discount_rate > 0 && (
              <span className="text-sm font-bold text-warn-red">
                {product.discount_rate}%
              </span>
            )}
            <span className="text-sm font-bold text-gray-600">
              {formatPrice(product.price)}원
            </span>
          </div>
          {product.discount_rate > 0 && (
            <p className="text-xs text-gray-300 line-through">
              {formatPrice(product.original_price)}원
            </p>
          )}
          <div className="flex items-center gap-1 mt-1">
            <span className="text-[10px] text-primary bg-primary-light px-1.5 py-0.5 rounded">
              AI분석 가능
            </span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
