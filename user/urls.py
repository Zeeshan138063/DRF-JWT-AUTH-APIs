from django.urls import path, include

from user.views import (
    UserViewSet,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    LogoutView,

)

from rest_framework import routers

# class ThisWillBeTheApiTitleView(routers.APIRootView):
#     """
#     This appears where the docstring goes!
#     """
#     pass
#
#
# class DocumentedRouter(routers.DefaultRouter):
#     APIRootView = ThisWillBeTheApiTitleView
#
#
# router = DocumentedRouter()
# router.register('users', UserViewSet)


router = routers.DefaultRouter()
router.register('users', UserViewSet)

from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token
)

'''
refresh_jwt_token
If JWT_ALLOW_REFRESH is True, non-expired tokens can be "refreshed" 
to obtain a brand new token with renewed expiration time. 

verify_jwt_token
API View that checks the veracity of a token, 
returning the token if it is valid.
'''

urlpatterns = [

    path('', include(router.urls)),
    path('login/', obtain_jwt_token, name="auth-login"),
    # path('login/',
    # ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer),
    # name="auth-login"),

    path('api-token-refresh/', refresh_jwt_token),
    path('api-token-verify/', verify_jwt_token),

    path('password/reset/', PasswordResetView.as_view(),
         name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
         name='rest_password_reset_confirm'),
    path('password/change/', PasswordChangeView.as_view(),
         name='rest_password_change'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),

]
# urlpatterns+=   url(r'^', include(router.urls)),
urlpatterns += router.urls
