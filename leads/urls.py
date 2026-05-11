from django.urls import path
from .views import (
    LeadListView,
    LeadCreateView,
    LeadUpdateView,
    LeadDeleteView,
    CategoryListView,
    CategoryDetailView,
    LeadCategoryUpdateView,
    CategoryCreateView,
    LeadSelectAgentView,
    LeadMessageUpdateView,
    LeadReplyUpdateView,
)

app_name = "leads"

urlpatterns = [
    path("", LeadListView.as_view(), name="home_page"),
    path("create/", LeadCreateView.as_view(), name="create_lead"),
    path("update/<int:pk>/", LeadUpdateView.as_view(), name="update_lead"),
    path("delete/<int:pk>/", LeadDeleteView.as_view(), name="delete_lead"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/<int:pk>", CategoryDetailView.as_view(), name="category_detail"),
    path("category/", CategoryCreateView.as_view(), name="category_create"),
    path("select-agent/<int:pk>/", LeadSelectAgentView.as_view(), name="select_agent"),
    path(
        "category_update/<int:pk>",
        LeadCategoryUpdateView.as_view(),
        name="lead_category_update",
    ),
    path("message/<int:pk>/", LeadMessageUpdateView.as_view(), name="lead_message_update"),
    path("reply/<int:pk>/", LeadReplyUpdateView.as_view(), name="lead_reply_update"),
]
