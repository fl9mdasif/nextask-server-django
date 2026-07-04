from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import AnnotationImage, Polygon
from .serializers import AnnotationImageSerializer, PolygonSerializer


# ── /api/annotate/images/ ─────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def image_list(request):

    # ── GET — list all images for current user ────────────────────────────────
    if request.method == 'GET':
        images = AnnotationImage.objects.filter(user=request.user)
        serializer = AnnotationImageSerializer(
            images, many=True, context={'request': request}
        )
        return Response({'success': True, 'data': serializer.data})

    # ── POST — upload new image ───────────────────────────────────────────────
    if request.method == 'POST':
        serializer = AnnotationImageSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {'success': True, 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# ── /api/annotate/images/<id>/ ────────────────────────────────────────────────

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def image_detail(request, pk):
    try:
        image = AnnotationImage.objects.get(pk=pk, user=request.user)
    except AnnotationImage.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Image not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # ── GET — single image with polygons ─────────────────────────────────────
    if request.method == 'GET':
        serializer = AnnotationImageSerializer(image, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

    # ── DELETE — remove image ─────────────────────────────────────────────────
    if request.method == 'DELETE':
        image.delete()
        return Response({'success': True, 'message': 'Image deleted'})


# ── /api/annotate/images/<id>/polygons/ ──────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def polygon_list(request, pk):
    try:
        image = AnnotationImage.objects.get(pk=pk, user=request.user)
    except AnnotationImage.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Image not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # ── GET — all polygons for this image ─────────────────────────────────────
    if request.method == 'GET':
        polygons = image.polygons.all()
        serializer = PolygonSerializer(polygons, many=True)
        return Response({'success': True, 'data': serializer.data})

    # ── POST — save new polygon ───────────────────────────────────────────────
    if request.method == 'POST':
        serializer = PolygonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(image=image)
            return Response(
                {'success': True, 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# ── /api/annotate/polygons/<id>/ ─────────────────────────────────────────────

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def polygon_detail(request, pk):
    try:
        # Ensure the polygon belongs to an image owned by this user
        polygon = Polygon.objects.get(pk=pk, image__user=request.user)
    except Polygon.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Polygon not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    polygon.delete()
    return Response({'success': True, 'message': 'Polygon deleted'})
