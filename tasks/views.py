from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list(request):

    # ── GET — list tasks ──────────────────────────────
    if request.method == 'GET':
        date = request.query_params.get('date')

        tasks = Task.objects.filter(user=request.user)

        if date:
            tasks = tasks.filter(due_date=date)

        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    # ── POST — create task ────────────────────────────
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):

    # task exists + belongs to user check
    try:
        task = Task.objects.get(pk=pk, user=request.user)
    except Task.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # ── GET ───────────────────────────────────────────
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response({'success': True, 'data': serializer.data})

    # ── PATCH — update task ───────────────────────────
    if request.method == 'PATCH':
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── DELETE ────────────────────────────────────────
    if request.method == 'DELETE':
        task.delete()
        return Response({'success': True, 'message': 'Task deleted'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def task_reorder(request, pk):
    """Drag & drop — update status + order"""
    try:
        task = Task.objects.get(pk=pk, user=request.user)
    except Task.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    new_status = request.data.get('status')
    new_order  = request.data.get('order')

    if new_status:
        task.status = new_status
    if new_order is not None:
        task.order = new_order

    task.save()
    serializer = TaskSerializer(task)
    return Response({'success': True, 'data': serializer.data})