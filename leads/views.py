from django.shortcuts import reverse, redirect, get_object_or_404
from .models import Lead, Category
from .forms import (
    LeadModelForm,
    CustomUserCreationForm,
    LeadCategoryUpdateForm,
    CreateCategoryForm,
    LeadUserCreationForm,
    LeadMessageForm,
    LeadReplyForm,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from agent.mixins import OrganizerAndLoginRequiredMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views import generic
from django.db.models import Count, Q


class SignupChoiceView(generic.TemplateView):
    template_name = "registration/signup_choice.html"

class OrganizerSignupView(CreateView):
    template_name = "registration/organizer_signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")

class LeadSignupView(CreateView):
    template_name = "registration/lead_signup.html"
    form_class = LeadUserCreationForm

    def get_success_url(self):
        return reverse("login")

class LeadSelectAgentView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        if request.user.role != "lead":
            return redirect("leads:home_page")
        
        from agent.models import Agent
        agent_pk = kwargs.get("pk")
        agent = get_object_or_404(Agent, pk=agent_pk, owner=request.user.lead_profile.owner)
        
        lead_profile = request.user.lead_profile
        lead_profile.agent = agent
        lead_profile.save()
        return redirect("leads:home_page")


class LeadListView(LoginRequiredMixin, ListView):
    context_object_name = "leads"

    def get_template_names(self):
        if self.request.user.role == "lead":
            return ["agents/agent_list.html"]
        return ["home_page.html"]

    def get_queryset(self):
        request = self.request
        query = request.GET.get("search")

        if request.user.role == "organizer":
            queryset = Lead.objects.filter(owner=request.user, agent__isnull=False)
        elif request.user.role == "lead":
            from agent.models import Agent
            queryset = Agent.objects.filter(owner=request.user.lead_profile.owner)
            return queryset
        else:
            queryset = Lead.objects.filter(
                owner=request.user.manager.owner, agent__manager=request.user
            )

        if query:
            queryset = queryset.filter(first_name__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        request = self.request
        if request.user.role == "lead":
            context["object_list"] = context["leads"]
            return context
        
        query = request.GET.get("search_unassigned")
        if request.user.role == "organizer":
            queryset = Lead.objects.filter(Q(owner=request.user) | Q(owner__isnull=True), agent__isnull=True)
            context.update({"unassigned_leads": queryset})
            if query:
                queryset = queryset.filter(first_name__icontains=query)
                context.update({"unassigned_leads": queryset})
        return context


class LeadCreateView(OrganizerAndLoginRequiredMixin, CreateView):
    template_name = "create_lead.html"
    form_class = LeadModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        # if self.request.user.role == "organizer":
        form.instance.owner = self.request.user
        # else:
        #     form.instance.agent = self.request.user.manager
        #     form.instance.owner = self.request.user.manager.owner
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("leads:home_page")


class LeadUpdateView(OrganizerAndLoginRequiredMixin, UpdateView):
    template_name = "update_lead.html"
    form_class = LeadModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_queryset(self):
        user = self.request.user

        # if user.role == "organizer":
        return Lead.objects.filter(owner=user)
        # else:
        #     return Lead.objects.filter(owner=user.manager.owner, agent__manager=user)

    def get_success_url(self):
        return reverse("leads:home_page")


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "delete_lead.html"

    def get_queryset(self):
        user = self.request.user

        if user.role == "organizer":
            return Lead.objects.filter(owner=user)
        else:
            return Lead.objects.filter(owner=user.manager.owner, agent__manager=user)

    def get_success_url(self):
        return reverse("leads:home_page")


class CategoryListView(OrganizerAndLoginRequiredMixin, generic.ListView):
    template_name = "category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        queryset = Lead.objects.filter(owner=user)

        context.update(
            {
                "unassigned_lead_count": queryset.filter(category__isnull=True).count(),
            }
        )
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(owner=user)
        return queryset.annotate(lead_count=Count("leads"))


class CategoryDetailView(OrganizerAndLoginRequiredMixin, generic.DetailView):
    template_name = "category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        leads = self.get_object().leads.all()
        context.update({"leads": leads})
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(owner=user)
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user

        if user.role == "organizer":
            queryset = Lead.objects.filter(owner=user)
        else:
            queryset = Lead.objects.filter(
                owner=user.manager.owner, agent__manager=user
            )
        return queryset

    def get_success_url(self):
        return reverse("leads:home_page")


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "create_category.html"
    form_class = CreateCategoryForm
    model = Category

    def form_valid(self, form):
        user = self.request.user
        if user.role == "organizer":
            form.instance.owner = user
        else:
            form.instance.owner = user.manager.owner
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("leads:home_page")

class LeadMessageUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "lead_message_update.html"
    form_class = LeadMessageForm

    def get_queryset(self):
        return Lead.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("leads:home_page")

class LeadReplyUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "lead_reply_update.html"
    form_class = LeadReplyForm

    def get_queryset(self):
        user = self.request.user
        if user.role == "organizer":
            return Lead.objects.filter(owner=user)
        else:
            return Lead.objects.filter(owner=user.manager.owner, agent__manager=user)

    def get_success_url(self):
        return reverse("leads:home_page")
