"""Tests for utility functions."""
import pytest

from app.utils.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.utils.pagination import PageResponse, create_page_response


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_not_found_exception_default(self):
        """Test NotFoundException with default message."""
        exc = NotFoundException()
        assert exc.status_code == 404
        assert exc.detail == "Resource not found"

    def test_not_found_exception_custom(self):
        """Test NotFoundException with custom message."""
        exc = NotFoundException(detail="User not found")
        assert exc.status_code == 404
        assert exc.detail == "User not found"

    def test_unauthorized_exception(self):
        """Test UnauthorizedException."""
        exc = UnauthorizedException()
        assert exc.status_code == 401
        assert exc.detail == "Unauthorized"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_unauthorized_exception_custom(self):
        """Test UnauthorizedException with custom message."""
        exc = UnauthorizedException(detail="Invalid token")
        assert exc.status_code == 401
        assert exc.detail == "Invalid token"

    def test_forbidden_exception(self):
        """Test ForbiddenException."""
        exc = ForbiddenException()
        assert exc.status_code == 403
        assert exc.detail == "Forbidden"

    def test_bad_request_exception(self):
        """Test BadRequestException."""
        exc = BadRequestException()
        assert exc.status_code == 400
        assert exc.detail == "Bad request"

    def test_conflict_exception(self):
        """Test ConflictException."""
        exc = ConflictException()
        assert exc.status_code == 409
        assert exc.detail == "Resource already exists"

    def test_app_exception_custom(self):
        """Test AppException with custom values."""
        exc = AppException(
            status_code=418,
            detail="I'm a teapot",
            headers={"X-Custom": "Header"}
        )
        assert exc.status_code == 418
        assert exc.detail == "I'm a teapot"
        assert exc.headers == {"X-Custom": "Header"}


class TestPaginationUtils:
    """Test pagination utility functions."""

    def test_create_page_response_first_page(self):
        """Test creating page response for first page."""
        items = [1, 2, 3, 4, 5]
        response = create_page_response(
            items=items,
            total=20,
            page=1,
            page_size=5
        )

        assert isinstance(response, PageResponse)
        assert response.items == items
        assert response.total == 20
        assert response.page == 1
        assert response.page_size == 5
        assert response.has_next is True
        assert response.has_prev is False

    def test_create_page_response_middle_page(self):
        """Test creating page response for middle page."""
        items = [6, 7, 8, 9, 10]
        response = create_page_response(
            items=items,
            total=20,
            page=2,
            page_size=5
        )

        assert response.items == items
        assert response.total == 20
        assert response.page == 2
        assert response.page_size == 5
        assert response.has_next is True
        assert response.has_prev is True

    def test_create_page_response_last_page(self):
        """Test creating page response for last page."""
        items = [16, 17, 18, 19, 20]
        response = create_page_response(
            items=items,
            total=20,
            page=4,
            page_size=5
        )

        assert response.items == items
        assert response.total == 20
        assert response.page == 4
        assert response.page_size == 5
        assert response.has_next is False
        assert response.has_prev is True

    def test_create_page_response_single_page(self):
        """Test creating page response when all items fit on one page."""
        items = [1, 2, 3]
        response = create_page_response(
            items=items,
            total=3,
            page=1,
            page_size=10
        )

        assert response.items == items
        assert response.total == 3
        assert response.page == 1
        assert response.page_size == 10
        assert response.has_next is False
        assert response.has_prev is False

    def test_create_page_response_empty(self):
        """Test creating page response with no items."""
        items = []
        response = create_page_response(
            items=items,
            total=0,
            page=1,
            page_size=10
        )

        assert response.items == []
        assert response.total == 0
        assert response.page == 1
        assert response.page_size == 10
        assert response.has_next is False
        assert response.has_prev is False

    def test_page_response_model(self):
        """Test PageResponse model validation."""
        response = PageResponse[int](
            items=[1, 2, 3],
            total=10,
            page=1,
            page_size=3,
            has_next=True,
            has_prev=False
        )

        assert response.items == [1, 2, 3]
        assert response.total == 10
        assert response.page == 1
        assert response.page_size == 3
        assert response.has_next is True
        assert response.has_prev is False
