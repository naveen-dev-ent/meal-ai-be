from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import json

from app.models.user import Stock, StockMovement, StockAlert
from app.schemas.stock_categories import (
    StockCategoryEnum,
    PetFoodTypeEnum,
    SpecialCareTypeEnum,
    StorageTypeEnum,
    StockPriorityEnum,
    AssignmentTypeEnum
)
from utils.api_logger import APILogger


class StockService:
    """Service for stock management and analytics"""
    
    def __init__(self):
        pass
    
    async def get_stock_analytics(
        self, 
        user_id: Optional[int], 
        family_id: Optional[int], 
        db: Session
    ) -> Dict[str, Any]:
        """Get comprehensive stock analytics with enhanced categorization"""
        try:
            # Get stock items
            query = db.query(Stock)
            
            if family_id:
                query = query.filter(Stock.family_id == family_id)
            else:
                query = query.filter(Stock.user_id == user_id)
            
            stock_items = query.all()
            
            if not stock_items:
                return self._empty_analytics()
            
            # Calculate enhanced analytics
            analytics = {
                'total_items': len(stock_items),
                'total_value': self._calculate_total_value(stock_items),
                'low_stock_items': self._count_low_stock_items(stock_items),
                'expiring_soon_items': self._count_expiring_soon_items(stock_items),
                'expired_items': self._count_expired_items(stock_items),
                
                # Enhanced categorization analytics
                'category_distribution': self._get_category_distribution(stock_items),
                'value_by_category': self._get_value_by_category(stock_items),
                'pet_food_analytics': self._get_pet_food_analytics(stock_items),
                'special_care_analytics': self._get_special_care_analytics(stock_items),
                'storage_distribution': self._get_storage_distribution(stock_items),
                'priority_distribution': self._get_priority_distribution(stock_items),
                'health_diet_analytics': self._get_health_diet_analytics(stock_items),
                'family_assignment_analytics': self._get_family_assignment_analytics(stock_items),
                
                # Existing analytics
                'consumption_trends': self._get_consumption_trends(stock_items, db),
                'expiry_risk': self._get_expiry_risk(stock_items),
                'stock_alerts': self._get_stock_alerts(stock_items, db)
            }
            
            return analytics
            
        except Exception as e:
            raise Exception(f"Failed to get stock analytics: {str(e)}")
    
    async def check_stock_alerts(
        self, 
        user_id: Optional[int], 
        family_id: Optional[int], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for stock items that need alerts"""
        try:
            alerts = []
            
            # Get stock items
            query = db.query(Stock)
            
            if family_id:
                query = query.filter(Stock.family_id == family_id)
            else:
                query = query.filter(Stock.user_id == user_id)
            
            stock_items = query.all()
            
            for item in stock_items:
                # Check low stock with enhanced priority logic
                if item.current_quantity <= item.minimum_quantity:
                    priority = self._calculate_alert_priority(item)
                    alerts.append({
                        'type': 'low_stock',
                        'priority': priority,
                        'message': f"{item.item_name} is running low (Current: {item.current_quantity} {item.unit}, Min: {item.minimum_quantity} {item.unit})",
                        'stock_id': item.id,
                        'item_name': item.item_name,
                        'category': item.category,
                        'is_special_care': item.is_special_care_item,
                        'is_pet_food': item.is_pet_food,
                        'priority_level': item.priority_level
                    })
                
                # Check expiring items
                if item.expiry_date:
                    days_until_expiry = (item.expiry_date - date.today()).days
                    
                    if days_until_expiry < 0:
                        alerts.append({
                            'type': 'expired',
                            'priority': 'critical',
                            'message': f"{item.item_name} has expired on {item.expiry_date}",
                            'stock_id': item.id,
                            'item_name': item.item_name
                        })
                    elif days_until_expiry <= 3:
                        alerts.append({
                            'type': 'expiring_soon',
                            'priority': 'high',
                            'message': f"{item.item_name} expires in {days_until_expiry} days",
                            'stock_id': item.id,
                            'item_name': item.item_name
                        })
                    elif days_until_expiry <= 7:
                        alerts.append({
                            'type': 'expiring_soon',
                            'priority': 'medium',
                            'message': f"{item.item_name} expires in {days_until_expiry} days",
                            'stock_id': item.id,
                            'item_name': item.item_name
                        })
            
            return alerts
            
        except Exception as e:
            raise Exception(f"Failed to check stock alerts: {str(e)}")
    
    async def record_stock_movement(
        self, 
        stock_id: int, 
        quantity_change: float, 
        movement_type: str, 
        reason: Optional[str], 
        db: Session,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Record a stock movement and update stock levels"""
        try:
            # Get stock item
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock:
                APILogger.log_error(f"Stock movement failed - stock item not found: {stock_id}")
                raise ValueError("Stock item not found")
            
            # Calculate new quantity
            new_quantity = stock.current_quantity + quantity_change
            
            if new_quantity < 0:
                APILogger.log_error(f"Stock movement failed - negative quantity: stock_id={stock_id}, new_quantity={new_quantity}")
                raise ValueError("Stock quantity cannot be negative")
            
            # Update stock quantity
            stock.current_quantity = new_quantity
            stock.updated_at = datetime.utcnow()
            
            # Create movement record
            movement = StockMovement(
                stock_id=stock_id,
                quantity_change=quantity_change,
                movement_type=movement_type,
                reason=reason,
                date=date.today()
            )
            
            db.add(movement)
            db.commit()
            
            APILogger.log_database_operation("CREATE", "stock_movement", True, user_id)
            APILogger.log_database_operation("UPDATE", "stock_quantity", True, user_id)
            
            # Check if alert is needed
            alert_needed = self._check_alert_needed(stock)
            
            return {
                'movement_id': movement.id,
                'new_quantity': new_quantity,
                'alert_needed': alert_needed,
                'message': f"Stock updated successfully. New quantity: {new_quantity} {stock.unit}"
            }
            
        except Exception as e:
            db.rollback()
            APILogger.log_database_operation("CREATE", "stock_movement", False, user_id)
            APILogger.log_error(f"Stock movement failed: {str(e)}")
            raise Exception(f"Failed to record stock movement: {str(e)}")
    
    async def get_stock_recommendations(
        self, 
        user_id: Optional[int], 
        family_id: Optional[int], 
        db: Session
    ) -> Dict[str, Any]:
        """Get stock recommendations based on usage patterns and preferences"""
        try:
            recommendations = {
                'restock_items': [],
                'reduce_items': [],
                'new_items': [],
                'expiry_management': []
            }
            
            # Get stock items
            query = db.query(Stock)
            
            if family_id:
                query = query.filter(Stock.family_id == family_id)
            else:
                query = query.filter(Stock.user_id == user_id)
            
            stock_items = query.all()
            
            for item in stock_items:
                # Enhanced restock recommendations
                if item.current_quantity <= item.minimum_quantity:
                    priority = self._calculate_restock_priority(item)
                    recommendations['restock_items'].append({
                        'item_name': item.item_name,
                        'current_quantity': item.current_quantity,
                        'recommended_quantity': item.minimum_quantity * 2,
                        'priority': priority,
                        'category': item.category,
                        'is_special_care': item.is_special_care_item,
                        'is_pet_food': item.is_pet_food,
                        'storage_type': item.storage_type,
                        'assignment_type': item.assignment_type
                    })
                
                # Reduce stock recommendations
                if item.current_quantity > item.minimum_quantity * 3:
                    recommendations['reduce_items'].append({
                        'item_name': item.item_name,
                        'current_quantity': item.current_quantity,
                        'recommended_quantity': item.minimum_quantity * 2,
                        'reason': 'Overstocked'
                    })
                
                # Expiry management
                if item.expiry_date and item.is_perishable:
                    days_until_expiry = (item.expiry_date - date.today()).days
                    if days_until_expiry <= 7:
                        recommendations['expiry_management'].append({
                            'item_name': item.item_name,
                            'days_until_expiry': days_until_expiry,
                            'action': 'Use soon' if days_until_expiry > 0 else 'Discard',
                            'priority': 'high' if days_until_expiry <= 3 else 'medium'
                        })
            
            return recommendations
            
        except Exception as e:
            raise Exception(f"Failed to get stock recommendations: {str(e)}")
    
    def _empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure with enhanced categorization"""
        return {
            'total_items': 0,
            'total_value': 0,
            'low_stock_items': 0,
            'expiring_soon_items': 0,
            'expired_items': 0,
            'category_distribution': {},
            'value_by_category': {},
            'pet_food_analytics': {},
            'special_care_analytics': {},
            'storage_distribution': {},
            'priority_distribution': {},
            'health_diet_analytics': {},
            'family_assignment_analytics': {},
            'consumption_trends': {},
            'expiry_risk': [],
            'stock_alerts': []
        }
    
    def _calculate_total_value(self, stock_items: List[Stock]) -> float:
        """Calculate total value of stock items"""
        total_value = 0
        for item in stock_items:
            if item.price_per_unit:
                total_value += item.price_per_unit * item.current_quantity
        return round(total_value, 2)
    
    def _count_low_stock_items(self, stock_items: List[Stock]) -> int:
        """Count items that are below minimum quantity"""
        return len([item for item in stock_items if item.current_quantity <= item.minimum_quantity])
    
    def _count_expiring_soon_items(self, stock_items: List[Stock]) -> int:
        """Count items expiring within 7 days"""
        tomorrow = date.today() + timedelta(days=1)
        return len([item for item in stock_items if item.expiry_date and item.expiry_date <= tomorrow + timedelta(days=6)])
    
    def _count_expired_items(self, stock_items: List[Stock]) -> int:
        """Count expired items"""
        return len([item for item in stock_items if item.expiry_date and item.expiry_date < date.today()])
    
    def _get_category_distribution(self, stock_items: List[Stock]) -> Dict[str, int]:
        """Get distribution of items by category"""
        distribution = {}
        for item in stock_items:
            distribution[item.category] = distribution.get(item.category, 0) + 1
        return distribution
    
    def _get_value_by_category(self, stock_items: List[Stock]) -> Dict[str, float]:
        """Get total value by category"""
        value_by_category = {}
        for item in stock_items:
            if item.price_per_unit:
                category_value = item.price_per_unit * item.current_quantity
                value_by_category[item.category] = value_by_category.get(item.category, 0) + category_value
        return {k: round(v, 2) for k, v in value_by_category.items()}
    
    def _get_consumption_trends(self, stock_items: List[Stock], db: Session) -> Dict[str, float]:
        """Get consumption trends (placeholder - would need historical movement data)"""
        # This is a simplified version. In a real implementation, you would:
        # 1. Query StockMovement table for historical data
        # 2. Calculate consumption rates over time
        # 3. Identify trends and patterns
        
        trends = {}
        for item in stock_items:
            # Mock consumption rate (0.1 kg per day average)
            trends[item.item_name] = round(0.1, 2)
        
        return trends
    
    def _get_expiry_risk(self, stock_items: List[Stock]) -> List[Dict[str, Any]]:
        """Get items with high expiry risk"""
        expiry_risk = []
        
        for item in stock_items:
            if item.expiry_date:
                days_until_expiry = (item.expiry_date - date.today()).days
                
                if days_until_expiry <= 7:
                    risk_level = 'high' if days_until_expiry <= 3 else 'medium'
                    
                    expiry_risk.append({
                        'item_name': item.item_name,
                        'days_until_expiry': days_until_expiry,
                        'current_quantity': item.current_quantity,
                        'priority': risk_level,
                        'action_required': 'Use immediately' if days_until_expiry <= 1 else 'Plan usage'
                    })
        
        # Sort by priority and days until expiry
        expiry_risk.sort(key=lambda x: (x['priority'] == 'high', x['days_until_expiry']))
        
        return expiry_risk
    
    def _get_stock_alerts(self, stock_items: List[Stock], db: Session) -> List[Dict[str, Any]]:
        """Get active stock alerts"""
        try:
            stock_ids = [item.id for item in stock_items]
            
            if not stock_ids:
                return []
            
            alerts = db.query(StockAlert).filter(
                StockAlert.stock_id.in_(stock_ids),
                StockAlert.is_resolved == False
            ).order_by(StockAlert.priority.desc(), StockAlert.created_at.desc()).all()
            
            return [
                {
                    'id': alert.id,
                    'stock_id': alert.stock_id,
                    'alert_type': alert.alert_type,
                    'message': alert.message,
                    'priority': alert.priority,
                    'created_at': alert.created_at
                }
                for alert in alerts
            ]
            
        except Exception as e:
            print(f"Error getting stock alerts: {str(e)}")
            return []
    
    def _check_alert_needed(self, stock: Stock) -> bool:
        """Check if an alert is needed for a stock item"""
        # Alert needed for low stock
        if stock.current_quantity <= stock.minimum_quantity:
            return True
        
        # Alert needed for expiring items
        if stock.expiry_date and stock.is_perishable:
            days_until_expiry = (stock.expiry_date - date.today()).days
            if days_until_expiry <= 3:
                return True
        
        return False
    
    def _calculate_alert_priority(self, stock: Stock) -> str:
        """Calculate alert priority based on enhanced categorization"""
        if stock.priority_level == StockPriorityEnum.CRITICAL:
            return 'critical'
        elif stock.is_special_care_item or stock.priority_level == StockPriorityEnum.URGENT:
            return 'high'
        elif stock.is_pet_food or stock.priority_level == StockPriorityEnum.IMPORTANT:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_restock_priority(self, stock: Stock) -> str:
        """Calculate restock priority based on enhanced categorization"""
        if stock.priority_level == StockPriorityEnum.CRITICAL or stock.is_special_care_item:
            return 'critical'
        elif stock.priority_level == StockPriorityEnum.URGENT or stock.is_pet_food:
            return 'high'
        elif stock.priority_level == StockPriorityEnum.IMPORTANT:
            return 'medium'
        else:
            return 'low'
    
    def _get_pet_food_analytics(self, stock_items: List[Stock]) -> Dict[str, Any]:
        """Get pet food specific analytics"""
        pet_items = [item for item in stock_items if item.is_pet_food]
        
        if not pet_items:
            return {'total_items': 0, 'total_value': 0, 'pet_types': {}}
        
        pet_types = {}
        total_value = 0
        
        for item in pet_items:
            pet_type = item.pet_type or 'unknown'
            if pet_type not in pet_types:
                pet_types[pet_type] = {'count': 0, 'value': 0}
            
            pet_types[pet_type]['count'] += 1
            if item.price_per_unit:
                value = item.price_per_unit * item.current_quantity
                pet_types[pet_type]['value'] += value
                total_value += value
        
        return {
            'total_items': len(pet_items),
            'total_value': round(total_value, 2),
            'pet_types': pet_types
        }
    
    def _get_special_care_analytics(self, stock_items: List[Stock]) -> Dict[str, Any]:
        """Get special care items analytics"""
        special_care_items = [item for item in stock_items if item.is_special_care_item]
        
        if not special_care_items:
            return {'total_items': 0, 'total_value': 0, 'care_types': {}, 'assigned_users': {}}
        
        care_types = {}
        assigned_users = {}
        total_value = 0
        
        for item in special_care_items:
            # Parse special care types from JSON
            if item.special_care_types:
                try:
                    types = json.loads(item.special_care_types) if isinstance(item.special_care_types, str) else item.special_care_types
                    for care_type in types:
                        care_types[care_type] = care_types.get(care_type, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    care_types['unknown'] = care_types.get('unknown', 0) + 1
            
            # Track assigned users
            if item.special_care_user_id:
                user_id = str(item.special_care_user_id)
                assigned_users[user_id] = assigned_users.get(user_id, 0) + 1
            
            # Calculate value
            if item.price_per_unit:
                total_value += item.price_per_unit * item.current_quantity
        
        return {
            'total_items': len(special_care_items),
            'total_value': round(total_value, 2),
            'care_types': care_types,
            'assigned_users': assigned_users
        }
    
    def _get_storage_distribution(self, stock_items: List[Stock]) -> Dict[str, int]:
        """Get distribution by storage type"""
        distribution = {}
        for item in stock_items:
            storage_type = item.storage_type or 'pantry'
            distribution[storage_type] = distribution.get(storage_type, 0) + 1
        return distribution
    
    def _get_priority_distribution(self, stock_items: List[Stock]) -> Dict[str, int]:
        """Get distribution by priority level"""
        distribution = {}
        for item in stock_items:
            priority = item.priority_level or 'important'
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution
    
    def _get_health_diet_analytics(self, stock_items: List[Stock]) -> Dict[str, Any]:
        """Get health and diet specific analytics"""
        analytics = {
            'organic_items': len([item for item in stock_items if item.is_organic]),
            'gluten_free_items': len([item for item in stock_items if item.is_gluten_free]),
            'vegan_items': len([item for item in stock_items if item.is_vegan]),
            'diabetic_friendly_items': len([item for item in stock_items if item.is_diabetic_friendly])
        }
        
        # Calculate values
        for category in ['organic', 'gluten_free', 'vegan', 'diabetic_friendly']:
            field_name = f'is_{category}'
            total_value = sum(
                item.price_per_unit * item.current_quantity
                for item in stock_items
                if getattr(item, field_name, False) and item.price_per_unit
            )
            analytics[f'{category}_value'] = round(total_value, 2)
        
        return analytics
    
    def _get_family_assignment_analytics(self, stock_items: List[Stock]) -> Dict[str, Any]:
        """Get family assignment analytics"""
        assignment_distribution = {}
        user_assignments = {}
        
        for item in stock_items:
            assignment_type = item.assignment_type or 'shared'
            assignment_distribution[assignment_type] = assignment_distribution.get(assignment_type, 0) + 1
            
            if item.user_id and assignment_type in ['exclusive', 'preferred']:
                user_id = str(item.user_id)
                if user_id not in user_assignments:
                    user_assignments[user_id] = {'exclusive': 0, 'preferred': 0}
                user_assignments[user_id][assignment_type] += 1
        
        return {
            'assignment_distribution': assignment_distribution,
            'user_assignments': user_assignments
        }
