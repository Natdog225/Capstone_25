"""
CSV Upload API - Live Demo Feature (FIXED for Toast POS format)
Upload new sales data and watch dashboard update in real-time via WebSocket
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Dict
import pandas as pd
from datetime import datetime
import logging
from io import StringIO
import asyncio
import random

from app.database.database import SessionLocal
from app.models.database_models import MenuItem, Order, OrderItem
from app.websocket.manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


async def process_csv_upload(file_content: str, filename: str):
    """Background task to process CSV and update database with live updates"""
    
    try:
        await manager.broadcast({
            'type': 'upload_started',
            'filename': filename,
            'message': f'Starting upload: {filename}',
            'progress': 0
        })
        await asyncio.sleep(0.5)
        
        # Parse CSV
        df = pd.read_csv(StringIO(file_content))
        logger.info(f"Parsed CSV: {len(df)} rows, columns: {list(df.columns)}")
        
        await manager.broadcast({
            'type': 'upload_progress',
            'message': f'📊 Found {len(df):,} records',
            'progress': 5
        })
        await asyncio.sleep(0.3)
        
        # Process the CSV
        await process_toast_items_csv(df, filename)
        
        await manager.broadcast({
            'type': 'upload_complete',
            'message': f'✅ Successfully loaded data from {filename}!',
            'progress': 100,
            'filename': filename
        })
        
        await asyncio.sleep(1)
        await manager.broadcast({
            'type': 'refresh_dashboard',
            'message': 'Dashboard updated with new data'
        })
        
    except Exception as e:
        logger.error(f"Upload processing error: {e}", exc_info=True)
        await manager.broadcast({
            'type': 'upload_error',
            'message': f'❌ Upload failed: {str(e)}',
            'error': str(e)
        })


async def process_toast_items_csv(df: pd.DataFrame, filename: str):
    """Process Toast POS Items CSV format"""
    
    db = SessionLocal()
    
    try:
        logger.info(f"CSV columns: {list(df.columns)}")
        
        # CRITICAL: Filter out summary rows (where Item is empty/NaN)
        df = df[df['Item'].notna() & (df['Item'] != '')].copy()
        
        logger.info(f"After filtering summary rows: {len(df)} items")
        
        if len(df) == 0:
            raise ValueError("No items found in CSV (all rows appear to be summaries)")
        
        await manager.broadcast({
            'type': 'upload_progress',
            'message': f'📊 Processing {len(df)} menu items...',
            'progress': 10
        })
        await asyncio.sleep(0.3)
        
        # Extract data with proper column names
        df['item_name'] = df['Item'].astype(str).str.strip()
        df['category'] = df['Sales Category'].fillna('General').astype(str)
        
        # Get quantity and price
        df['quantity'] = pd.to_numeric(df['Qty sold'], errors='coerce').fillna(1).astype(int)
        df['gross_sales'] = pd.to_numeric(df['Gross sales'], errors='coerce').fillna(0)
        
        # Calculate unit price
        df['unit_price'] = (df['gross_sales'] / df['quantity']).replace(
            [float('inf'), float('-inf')], 10.0
        ).fillna(10.0).round(2)
        
        # Clean data
        df = df[df['quantity'] > 0].copy()
        
        logger.info(f"Valid items after cleaning: {len(df)}")
        
        await manager.broadcast({
            'type': 'upload_progress',
            'message': '🍽️ Loading menu items into database...',
            'progress': 20
        })
        await asyncio.sleep(0.3)
        
        # ==================================================
        # STEP 1: Load Menu Items
        # ==================================================
        unique_items = df[['item_name', 'category', 'unit_price']].drop_duplicates(subset=['item_name'])
        item_map = {}
        new_items_count = 0
        
        for idx, row in unique_items.iterrows():
            item_name = str(row['item_name']).strip()
            
            existing = db.query(MenuItem).filter(
                MenuItem.item_name == item_name
            ).first()
            
            if existing:
                item_map[item_name] = existing.id
            else:
                new_item = MenuItem(
                    item_name=item_name,
                    category=str(row['category']),
                    price=float(row['unit_price']),
                    is_active=True
                )
                db.add(new_item)
                db.flush()
                item_map[item_name] = new_item.id
                new_items_count += 1
        
        db.commit()
        
        await manager.broadcast({
            'type': 'upload_progress',
            'message': f'✓ Loaded {len(item_map)} items ({new_items_count} new)',
            'progress': 40
        })
        await asyncio.sleep(0.3)
        
        # ==================================================
        # STEP 2: Create Orders
        # ==================================================
        await manager.broadcast({
            'type': 'upload_progress',
            'message': '📝 Generating orders from sales data...',
            'progress': 50
        })
        await asyncio.sleep(0.3)
        
        # Extract month from filename
        month = 2  # default
        try:
            if filename[:2].isdigit():
                month = int(filename[:2])
        except:
            pass
        
        order_counter = db.query(Order).count() + 1
        orders_created = 0
        order_items = []
        
        random.seed(42)
        base_date = datetime(2025, month, 1, 12, 0, 0)
        
        # Create orders - one per item sold
        for idx, row in df.iterrows():
            order_number = f"UPLOAD_{order_counter:06d}"
            
            # Distribute across month
            days_offset = idx % 28
            hours_offset = random.randint(11, 20)
            minutes_offset = random.randint(0, 59)
            
            timestamp = base_date.replace(
                day=min(days_offset + 1, 28),
                hour=hours_offset,
                minute=minutes_offset
            )
            
            item_name = str(row['item_name']).strip()
            quantity = int(row['quantity'])
            unit_price = float(row['unit_price'])
            order_total = quantity * unit_price
            
            # Create order
            new_order = Order(
                order_number=order_number,
                order_timestamp=timestamp,
                order_total=order_total,
                party_size=random.randint(1, 4)
            )
            db.add(new_order)
            db.flush()
            
            # Create order item
            item_id = item_map.get(item_name)
            if item_id:
                order_items.append(OrderItem(
                    order_id=new_order.id,
                    menu_item_id=item_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=order_total
                ))
            
            order_counter += 1
            orders_created += 1
            
            # Progress updates
            if orders_created % 10 == 0:
                progress = 50 + int((idx / len(df)) * 25)
                await manager.broadcast({
                    'type': 'upload_progress',
                    'message': f'Creating order {orders_created}/{len(df)}...',
                    'progress': progress
                })
        
        db.commit()
        
        await manager.broadcast({
            'type': 'upload_progress',
            'message': f'✓ Created {orders_created} orders',
            'progress': 80
        })
        await asyncio.sleep(0.3)
        
        # ==================================================
        # STEP 3: Save Order Items
        # ==================================================
        await manager.broadcast({
            'type': 'upload_progress',
            'message': '�� Saving order items...',
            'progress': 85
        })
        await asyncio.sleep(0.3)
        
        if order_items:
            db.bulk_save_objects(order_items)
            db.commit()
        
        await manager.broadcast({
            'type': 'upload_progress',
            'message': f'✓ Saved {len(order_items):,} order items',
            'progress': 95
        })
        
        logger.info(f"✅ Upload complete: {orders_created} orders, {len(order_items)} items from {filename}")
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}", exc_info=True)
        raise
    finally:
        db.close()


@router.post("/upload-csv")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict:
    """Upload sales CSV and update database in real-time"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files supported")
    
    try:
        content = await file.read()
        file_content = content.decode('utf-8')
        
        logger.info(f"📤 Received: {file.filename} ({len(file_content)} bytes)")
        
        background_tasks.add_task(process_csv_upload, file_content, file.filename)
        
        return {
            'status': 'processing',
            'filename': file.filename,
            'message': 'Upload started - watch for real-time updates'
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/upload-status")
async def get_upload_status() -> Dict:
    """Get upload status"""
    return {
        'status': 'ready',
        'connected_clients': len(manager.active_connections),
        'websocket_url': 'ws://localhost:8000/ws/dashboard'
    }


@router.delete("/clear-uploaded-data")
async def clear_uploaded_data() -> Dict:
    """Clear uploaded demo data (for resetting demo)"""
    
    db = SessionLocal()
    try:
        uploaded_orders = db.query(Order).filter(
            Order.order_number.like('UPLOAD_%')
        ).all()
        
        count = len(uploaded_orders)
        
        for order in uploaded_orders:
            db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
            db.delete(order)
        
        db.commit()
        
        await manager.broadcast({
            'type': 'refresh_dashboard',
            'message': f'Cleared {count} uploaded orders'
        })
        
        return {
            'status': 'success',
            'cleared_orders': count,
            'message': f'Demo reset - cleared {count} orders'
        }
        
    finally:
        db.close()
