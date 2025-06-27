from datetime import datetime
from typing import Any, Optional, TypedDict

from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.notification.models.model_notification import NotificationModel
from app.utils.types_utils.response_types import response_message


# Type definitions for request data
class CreateNotificationData(TypedDict):
    title: str
    content: str
    notification_type: str
    user_id: str


class UpdateNotificationData(TypedDict, total=False):
    title: Optional[str]
    content: Optional[str]
    notification_type: Optional[str]
    is_read: Optional[bool]
    read_at: Optional[datetime]


class NotificationFilter(TypedDict, total=False):
    id: Optional[str]
    user_id: Optional[str]
    notification_type: Optional[str]
    is_read: Optional[bool]


class NotificationQuery(TypedDict, total=False):
    limit: Optional[int]
    offset: Optional[int]
    order_by: Optional[str]
    order_direction: Optional[str]  # 'asc' or 'desc'


# Response types
class ResponseMessage(TypedDict):
    success_status: bool
    message: str
    error: Any
    data: Any
    doc_length: Optional[int]



class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_notification(self, data: CreateNotificationData) -> ResponseMessage:
        """Create a new notification"""
        try:
            notification = NotificationModel(
                title=data["title"],
                content=data["content"],
                notification_type=data["notification_type"],
                user_id=data["user_id"],
            )

            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)

            return response_message(
                success_status=True,
                message="Notification sent successfully",
                data={
                    "id": str(notification.id),
                    "title": notification.title,
                    "content": notification.content,
                    "notification_type": notification.notification_type,
                    "user_id": notification.user_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat()
                    if notification.created_at
                    else None,
                    "read_at": notification.read_at.isoformat()
                    if notification.read_at
                    else None,
                },
            )

        except SQLAlchemyError as e:
            await self.db.rollback()
            return response_message(
                success_status=False, message="Failed to send notification", error=e
            )
        except Exception as e:
            await self.db.rollback()
            return response_message(
                success_status=False, message="An unexpected error occurred", error=e
            )

    async def get_notification(
        self, filter_data: NotificationFilter
    ) -> ResponseMessage:
        """Get a single notification based on filter"""
        try:
            query = select(NotificationModel)

            # Build filter conditions
            conditions = []
            if filter_data.get("id"):
                conditions.append(NotificationModel.id == filter_data.get("id"))
            if filter_data.get("user_id"):
                conditions.append(NotificationModel.user_id == filter_data.get("user_id"))
            if filter_data.get("notification_type"):
                conditions.append(
                    NotificationModel.notification_type
                    == filter_data.get("notification_type")
                )
            if filter_data.get("is_read") is not None:
                conditions.append(NotificationModel.is_read == filter_data.get("is_read"))

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.db.execute(query)
            notification = result.scalar_one_or_none()

            if not notification:
                return response_message(
                    success_status=False,
                    message="Notification not found",
                    error="No notification matches the given criteria",
                )

            return response_message(
                success_status=True,
                message="Notification retrieved successfully",
                data={
                    "id": str(notification.id),
                    "title": notification.title,
                    "content": notification.content,
                    "notification_type": notification.notification_type,
                    "user_id": notification.user_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat()
                    if notification.created_at
                    else None,
                    "updated_at": notification.updated_at.isoformat()
                    if notification.updated_at
                    else None,
                    "read_at": notification.read_at.isoformat()
                    if notification.read_at
                    else None,
                },
            )

        except SQLAlchemyError as e:
            return response_message(
                success_status=False, message="Failed to retrieve notification", error=e
            )
        except Exception as e:
            return response_message(
                success_status=False, message="An unexpected error occurred", error=e
            )

    async def get_notifications(
        self, filter_data: NotificationFilter, query_params: NotificationQuery
    ) -> ResponseMessage:
        """Get multiple notifications with filtering and pagination"""
        try:
            query = select(NotificationModel)

            # Build filter conditions
            conditions = []
            if filter_data.get("user_id"):
                conditions.append(NotificationModel.user_id == filter_data.get("user_id"))
            if filter_data.get("notification_type"):
                conditions.append(
                    NotificationModel.notification_type
                    == filter_data.get("notification_type")
                )
            if filter_data.get("is_read") is not None:
                conditions.append(NotificationModel.is_read == filter_data.get("is_read"))

            if conditions:
                query = query.where(and_(*conditions))

            # Add ordering
            order_by = query_params.get("order_by") or "created_at"
            order_direction = query_params.get("order_direction", "desc")

            if isinstance(order_by, str) and hasattr(NotificationModel, order_by):
                order_column = getattr(NotificationModel, order_by)
                if str(order_direction).lower() == "desc":
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column.asc())

            # Get total count for pagination
            count_query = select(NotificationModel.id)
            if conditions:
                count_query = count_query.where(and_(*conditions))

            count_result = await self.db.execute(count_query)
            total_count = len(count_result.fetchall())

            # Add pagination
            if query_params.get("limit"):
                query = query.limit(query_params.get("limit"))
            if query_params.get("offset"):
                query = query.offset(query_params.get("offset"))

            result = await self.db.execute(query)
            notifications = result.scalars().all()

            notifications_data = []
            for notification in notifications:
                notifications_data.append({
                    "id": str(notification.id),
                    "title": notification.title,
                    "content": notification.content,
                    "notification_type": notification.notification_type,
                    "user_id": notification.user_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat()
                    if notification.created_at
                    else None,
                    "updated_at": notification.updated_at.isoformat()
                    if notification.updated_at
                    else None,
                    "read_at": notification.read_at.isoformat()
                    if notification.read_at
                    else None,
                })

            return response_message(
                success_status=True,
                message="Notifications retrieved successfully",
                data=notifications_data,
                doc_length=total_count,
            )

        except SQLAlchemyError as e:
            return response_message(
                success_status=False,
                message="Failed to retrieve notifications",
                error=e,
            )
        except Exception as e:
            return response_message(
                success_status=False, message="An unexpected error occurred", error=e
            )

    async def update_notification(
        self, update_data: UpdateNotificationData, filter_data: NotificationFilter
    ) -> ResponseMessage:
        """Update notification(s) based on filter"""
        try:
            # Build filter conditions
            conditions = []
            if filter_data.get("id"):
                conditions.append(NotificationModel.id == filter_data.get("id"))
            if filter_data.get("user_id"):
                conditions.append(NotificationModel.user_id == filter_data.get("user_id"))
            if filter_data.get("notification_type"):
                conditions.append(
                    NotificationModel.notification_type
                    == filter_data.get("notification_type")
                )
            if filter_data.get("is_read") is not None:
                conditions.append(NotificationModel.is_read == filter_data.get("is_read"))

            if not conditions:
                return response_message(
                    success_status=False,
                    message="No filter criteria provided for update",
                    error="At least one filter condition is required",
                )

            # Build update data
            update_values = {}
            if "title" in update_data:
                update_values["title"] = update_data["title"]
            if "content" in update_data:
                update_values["content"] = update_data["content"]
            if "notification_type" in update_data:
                update_values["notification_type"] = update_data["notification_type"]
            if "is_read" in update_data:
                update_values["is_read"] = update_data["is_read"]
            if "read_at" in update_data:
                update_values["read_at"] = update_data["read_at"]

            if not update_values:
                return response_message(
                    success_status=False,
                    message="No update data provided",
                    error="At least one field to update is required",
                )

            # Add updated_at timestamp
            update_values["updated_at"] = datetime.utcnow()

            query = (
                update(NotificationModel)
                .where(and_(*conditions))
                .values(**update_values)
            )
            result = await self.db.execute(query)
            await self.db.commit()

            if result.rowcount == 0:
                return response_message(
                    success_status=False,
                    message="No notifications found to update",
                    error="No notifications match the given criteria",
                )

            return response_message(
                success_status=True,
                message=f"Successfully updated {result.rowcount} notification(s)",
                data={"updated_count": result.rowcount},
            )

        except SQLAlchemyError as e:
            await self.db.rollback()
            return response_message(
                success_status=False, message="Failed to update notification", error=e
            )
        except Exception as e:
            await self.db.rollback()
            return response_message(
                success_status=False, message="An unexpected error occurred", error=e
            )

    async def delete_notification(
        self, filter_data: NotificationFilter
    ) -> ResponseMessage:
        """Delete notification(s) based on filter"""
        try:
            # Build filter conditions
            conditions = []
            if filter_data.get("id"):
                conditions.append(NotificationModel.id == filter_data.get("id"))
            if filter_data.get("user_id"):
                conditions.append(NotificationModel.user_id == filter_data.get("user_id"))
            if filter_data.get("notification_type"):
                conditions.append(
                    NotificationModel.notification_type
                    == filter_data.get("notification_type")
                )
            if filter_data.get("is_read") is not None:
                conditions.append(NotificationModel.is_read == filter_data.get("is_read"))

            if not conditions:
                return response_message(
                    success_status=False,
                    message="No filter criteria provided for deletion",
                    error="At least one filter condition is required",
                )

            query = delete(NotificationModel).where(and_(*conditions))
            result = await self.db.execute(query)
            await self.db.commit()

            if result.rowcount == 0:
                return response_message(
                    success_status=False,
                    message="No notifications found to delete",
                    error="No notifications match the given criteria",
                )

            return response_message(
                success_status=True,
                message=f"Successfully deleted {result.rowcount} notification(s)",
                data={"deleted_count": result.rowcount},
            )

        except SQLAlchemyError as e:
            await self.db.rollback()
            return response_message(
                success_status=False, message="Failed to delete notification", error=e
            )
        except Exception as e:
            await self.db.rollback()
            return response_message(
                success_status=False, message="An unexpected error occurred", error=e
            )

    async def get_notification_by_id(self, notification_id: str) -> ResponseMessage:
        """Get notification by ID"""
        return await self.get_notification({"id": notification_id})

    async def get_notifications_by_user_id(
        self, user_id: str, query_params: NotificationQuery
    ) -> ResponseMessage:
        """Get notifications for a specific user"""
        return await self.get_notifications({"user_id": user_id}, query_params)

    async def mark_notification_as_read(self, notification_id: str) -> ResponseMessage:
        """Mark a notification as read"""
        return await self.update_notification(
            {"is_read": True, "read_at": datetime.utcnow()}, {"id": notification_id}
        )

    async def mark_all_user_notifications_as_read(
        self, user_id: str
    ) -> ResponseMessage:
        """Mark all notifications for a user as read"""
        return await self.update_notification(
            {"is_read": True, "read_at": datetime.utcnow()},
            {"user_id": user_id, "is_read": False},
        )

    async def get_unread_notifications_count(self, user_id: str) -> ResponseMessage:
        """Get count of unread notifications for a user"""
        try:
            query = select(NotificationModel.id).where(
                and_(
                    NotificationModel.user_id == user_id,
                    NotificationModel.is_read == False,
                )
            )

            result = await self.db.execute(query)
            count = len(result.fetchall())

            return response_message(
                success_status=True,
                message="Unread notifications count retrieved successfully",
                data={"unread_count": count},
            )

        except SQLAlchemyError as e:
            return response_message(
                success_status=False,
                message="Failed to get unread notifications count",
                error=e,
            )
        except Exception as e:
            return response_message(
                success_status=False, message="An unexpected error occurred", error=e
            )
