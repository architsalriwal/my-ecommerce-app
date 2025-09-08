@api_view([POST])
@permission_classes([AllowAny])
def firebase_login(request):

    id_token = request.data.get('id_token')
    if not id_token:
        return Response({"error": "ID token not provided", status = status.HTTP_400_BAD_REQUEST})
    
    decoded_token = validate_firebase_token(id_token)
    if not decoded_token:
        return Response({"error:": "Invalid or expired token." , status = status.HTTP_401_UNAUTHORIZED})
    
    email = decoded_token.get('email')

    if not email:
        return Response({"error": "Email not found in token"}, status = status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
    try:
        user = User.objects.create_user(
            username = email,
            email = email,
            password = None
        )
    except Exception as e:
        return Response({"error": f"Failed to create user: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    token , created = Token.objects.get_or_create(user=user)

    return Response({
        "message": "Login successfull",
        "user_id": user.pk
        "token": token.key,
    })



    def validate_firebase_token(id_token):

        try:
            # The verify_id_token method handles all the validation and decoding.
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        
        except Exception as e:
            print(f"Firebase token validation failed: {e}")
            return None