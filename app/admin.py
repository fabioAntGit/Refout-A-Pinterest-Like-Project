from django import forms
from django.utils.html import format_html
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile, Post, Referencia, LikePost, FollowersCount, Notification, Comment, Report, VerifyReferences
from django.urls import reverse
from django.utils.http import urlencode
from django.shortcuts import HttpResponseRedirect


class ReportAdmin(admin.ModelAdmin):
    list_display = ['category', 'post', 'created']
    readonly_fields = ('post_description', 'get_post_references', 'display_image', 'category')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['post'].disabled = True  # Make the field read-only
        return form

    def post_description(self, obj):
        return obj.post.description

    def get_post_references(self, obj):
        references = obj.post.referencias.all()
        return ', '.join('{}: {}'.format(ref.category, ref.description) for ref in references)

    def display_image(self, obj):
        image_url = obj.post.image.url if obj.post.image else ''
        return format_html('<img style="border-radius:30px" src="{}"/>', image_url)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_delete_post_button'] = True
        return super().change_view(request, object_id, form_url, extra_context)

    

    def delete_post(self, request, object_id):
        # Get the Report object
        report = self.get_object(request, object_id)
        if report and report.post:
            post = report.post
            # Delete the associated post
            post.delete()
            self.message_user(request, 'The post has been deleted.')
            # Redirect back to the change page of the report
            return HttpResponseRedirect(reverse('admin:app_report_change', args=(object_id,)))

        # If no post is associated or the report doesn't exist, redirect to the report list page
        self.message_user(request, 'The report or associated post does not exist.')
        return HttpResponseRedirect(reverse('admin:app_report_changelist'))

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Remove the save and save and continue editing buttons from the fieldsets
        fieldsets = list(fieldsets)
        for i, (name, fieldset) in enumerate(fieldsets):
            if name == 'Save':
                fieldsets.pop(i)
                break
        return fieldsets

    def delete_report(self, obj):
        return format_html('<a class="button" href="{}">Delete Report</a>',
                           reverse('admin:app_report_delete', args=(obj.id,)))
    delete_report.short_description = 'Delete'

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        # Add the custom delete_report action to the list display
        list_display += ('delete_report',)
        return list_display

    fieldsets = (
        (None, {
            'fields': ('post','category', 'post_description', 'get_post_references', 'display_image'),
        }),
        ('Category', {
            'fields': (),
            'classes': ('collapse',),
            'description': 'Category field (non-editable)',
        }),
    )


admin.site.register(Report, ReportAdmin)
admin.site.register(Notification)
admin.site.register(FollowersCount)
admin.site.register(Referencia)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Post)
class VerifyReferencesAdmin(admin.ModelAdmin):
    readonly_fields = ('display_post_id', 'display_references',)
    list_display = ('id', 'display_verified',)

    def display_post_id(self, obj):
        post = obj.post
        image_url = post.image.url if post.image else ''
        post_change_url = reverse('admin:app_post_change', args=(post.id,))
        return format_html('<a href="{}"><img src="{}" style="border-radius: 40px;" /></a>', post_change_url, image_url)
    display_post_id.short_description = 'Post Image'

    def display_references(self, obj):
        references = obj.references.all()
        html = []
        for ref in references:
            link_field = self.get_link_field(ref)
            description = '<strong>{}</strong>'.format(ref.description)
            html.append('{0}: {1} {2}'.format(ref.category, description, link_field))
        return mark_safe('<br>'.join(html))

    def display_verified(self, obj):
        return obj.as_verified
    
    display_verified.short_description = 'Verified'
    display_verified.boolean = True
    
    def get_link_field(self, reference):
        if reference.link:
            return format_html('<input type="text" name="reference_link_{}" value="{}" />'.format(reference.id, reference.link))
        else:
            return format_html('<input type="text" name="reference_link_{}" value="" />'.format(reference.id))
    def save_model(self, request, obj, form, change):
        references = obj.references.all()
        for ref in references:
            reference_link = request.POST.get(f'reference_link_{ref.id}', None)
            if reference_link:
                ref.link = reference_link
                ref.save()
        super().save_model(request, obj, form, change)
        obj.as_verified = True  # Set as_verified to True
        obj.save()



    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets = (
            ('', {
                'fields': ('display_post_id',),
            }),
            ('', {
                'fields': ('display_references',),
            }),
            
        )
        return fieldsets

admin.site.register(VerifyReferences, VerifyReferencesAdmin)








