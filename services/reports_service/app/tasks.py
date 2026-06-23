import os
import httpx
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from app.scheduler import broker

@broker.register_task(name="generate_user_report")
async def generate_user_report(user_id: int):
    print(f"[Reports] Начинаем генерацию отчета для пользователя: {user_id}")

    MAIN_SERVICE_URL = os.getenv("MAIN_SERVICE_URL", "http://gym_backend:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_SERVICE_URL}/api/internal/workout-history/{user_id}", timeout=10.0)
            if response.status_code != 200:
                print(f"[Reports] Главный сервис вернул ошибку: {response.status_code}")
                return
            data = response.json()
    except Exception as e:
        print(f"[Reports] Не удалось получить данные от главного сервиса: {e}")
        return

    plt.figure(figsize=(6, 4))
    plt.plot(data["dates"], data["weights"], marker='o', color='purple', linewidth=2)
    plt.title("История рабочих весов в жиме лежа")
    plt.xlabel("Дата")
    plt.ylabel("Вес (кг)")
    plt.grid(True, linestyle='--', alpha=0.6)
    
    chart_path = f"/tmp/chart_{user_id}.png"
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

    pdf_path = f"/tmp/report_{user_id}.pdf"
    c = canvas.Canvas(pdf_path)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, f"Прогресс тренировок. Пользователь #{user_id}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, "Сгенерировано автоматически фоновым сервисом отчетов.")
    
    c.drawImage(chart_path, 50, 350, width=450, height=300)
    c.showPage()
    c.save()

    print(f"[Reports] PDF-отчет успешно сформирован: {pdf_path}")
    
    if os.path.exists(chart_path):
        os.remove(chart_path)
        
    # TODO: Сюда мы добавим отправку сообщения в RabbitMQ для сервиса уведомлений