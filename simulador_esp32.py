import serial
import time
import random
import math

# CONFIGURACIÓN: Transmite por el primer puerto virtual
PUERTO_SIMULADOR = 'COM10' 
BAUDIOS = 115200

try:
    ser = serial.Serial(PUERTO_SIMULADOR, BAUDIOS, timeout=1)
    print(f"🤖 Simulador de ESP32 corriendo en {PUERTO_SIMULADOR}...")
    print("Enviando datos de telemetría y audio simulados cada 30ms. Presiona Ctrl+C para detener.")
except:
    print(f"❌ No se pudo abrir el puerto {PUERTO_SIMULADOR}. Revisa la configuración de tus puertos virtuales.")
    exit()

t = 0
while True:
    try:
        t += 0.1
        
        # 1. Simular Profundidad (Ondulación suave bajando hasta 2 metros)
        profundidad = 1.0 + 0.5 * math.sin(t * 0.2) + random.uniform(-0.01, 0.01)
        
        # 2. Simular Aceleración Neta (Ruido base alrededor de 1.0G de la gravedad)
        # Cada cierto tiempo simula un pequeño golpe/vibración tectónica
        if random.random() > 0.95:
            acel_neta = random.uniform(1.8, 2.5) # ¡Impacto!
        else:
            acel_neta = 1.0 + random.uniform(-0.05, 0.05) # Ruido normal
            
        # 3. Simular Inclinación (Pitch y Roll balanceándose en el agua)
        pitch = 3.0 * math.sin(t * 0.5)
        roll = 2.0 * math.cos(t * 0.4)
        
        # 4. Simular Datos de la FFT del Piezoeléctrico (32 valores entre 0 y 255)
        # Si hubo impacto (acel_neta > 1.5), generamos frecuencias altas (pico de energía)
        fft_datos = []
        for i in range(32):
            if acel_neta > 1.5:
                val = int(random.uniform(150, 255)) # Ruido masivo en el espectro por golpe
            else:
                # Ruido base de baja frecuencia (las primeras barras de la FFT tienen más energía)
                val = int(max(0, (255 / (i + 1)) * random.uniform(0.1, 0.4)))
            fft_datos.append(str(val))
            
        fft_string = "-".join(fft_datos)

        # 5. Armar el paquete EXACTAMENTE igual al del ESP32 real
        # Formato: prof,acel,pitch,roll,fft1-fft2-...
        paquete = f"{profundidad:.2f},{acel_neta:.2f},{pitch:.1f},{roll:.1f},{fft_string}\n"
        
        # Enviar por el cable virtual
        ser.write(paquete.encode('utf-8'))
        
        time.sleep(0.03) # Frecuencia de envío idéntica a los 30ms del ESP32
        
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido.")
        ser.close()
        break