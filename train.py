import pickle
import tensorflow as tf
import numpy as np
import os
import json

# Configurar TensorFlow para usar la GPU si está disponible
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
if gpu_devices:
    for device in gpu_devices:
        tf.config.experimental.set_memory_growth(device, True)
    print("✅ GPU detectada y configurada para entrenamiento 🚀")
else:
    print("⚠️ No se detectó GPU, se usará CPU")

# Cargar los datos de entrenamiento
def cargar_datos(archivo):
    preguntas = []
    respuestas = []
    with open(archivo, 'r', encoding='utf-8') as file:
        for line in file:
            pregunta, respuesta = line.strip().split(';')
            preguntas.append(pregunta)
            respuestas.append(int(respuesta))  # Convertir respuestas a enteros
    return preguntas, np.array(respuestas)

# Preprocesar los datos
def preprocesar_datos(preguntas, respuestas):
    # Usar TextVectorization para mejor rendimiento
    tokenizer = tf.keras.layers.TextVectorization(output_mode='int')
    tokenizer.adapt(preguntas)
    x_train = tokenizer(preguntas)
    y_train = respuestas
    return x_train, y_train, tokenizer

# Construir el modelo LSTM
def construir_modelo(tokenizer, num_clases=3):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(input_dim=len(tokenizer.get_vocabulary()) + 1, output_dim=16, mask_zero=True),
        tf.keras.layers.LSTM(16),
        tf.keras.layers.Dense(num_clases, activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

# Entrenar el modelo
def entrenar_modelo(model, x_train, y_train):
    model.fit(x_train, y_train, epochs=20, batch_size=5, verbose=True)

# Guardar el modelo
def guardar_modelo(model, path='models/modelo.keras'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    model.save(path)
    print(f'✅ Modelo entrenado y guardado en {path} 🚀')

# Guardar el tokenizer completo
def guardar_tokenizer(tokenizer, path='models/tokenizer'):
    """Save tokenizer in multiple formats with proper Unicode handling"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # 1. Save vocabulary and configuration separately (most reliable)
    vocab = tokenizer.get_vocabulary()
    config = tokenizer.get_config()
    
    tokenizer_data = {
        "config": config,
        "vocabulary": vocab,
        "word_index": {word: idx for idx, word in enumerate(vocab)}
    }
    
    # Save JSON with explicit UTF-8 encoding
    with open(f"{path}.json", 'w', encoding='utf-8') as f:
        json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)
    
    # 2. Instead of pickling the layer directly, save its state that we can restore
    try:
        # Save vocabulary as text file with explicit UTF-8 encoding
        with open(f"{path}_vocab.txt", 'w', encoding='utf-8') as f:
            for word in vocab:
                f.write(f"{word}\n")
        print(f'✅ Tokenizer guardado en {path}.json y {path}_vocab.txt 🚀')
    except Exception as e:
        print(f"⚠️ Error al guardar vocabulario como texto: {e}")

# Probar el chatbot
def probar_chatbot(model, tokenizer):
    ''' 0: NECESITA_INFO (para frases que solicitan información)
        1: HALAGO (para frases que elogian el producto)
        2: NECESITA_TECNICO (para frases que indican problemas técnicos)'''
    while True:
        texto = input("Cliente dice: ")
        if texto.lower() == "salir":
            break
        texto_vectorizado = tokenizer([texto])
        prediccion = model.predict(texto_vectorizado)
        indice = np.argmax(prediccion)
        categorias = ["NECESITA_INFO", "HALAGO", "NECESITA_TECNICO"]
        categoria = categorias[indice]
        
        if categoria == "HALAGO":
            print("Respuesta: Halago al producto detectado")
        elif categoria == "NECESITA_INFO":
            print("Respuesta: Necesita información adicional sobre el producto")
        else:
            print("Respuesta: Necesita urgente asistencia técnica")

if __name__ == "__main__":
    archivo_datos = "data/dataset2.txt"  # Asegúrate de tener un archivo con el formato correcto
    preguntas, respuestas = cargar_datos(archivo_datos)
    x_train, y_train, tokenizer = preprocesar_datos(preguntas, respuestas)
    modelo = construir_modelo(tokenizer)
    entrenar_modelo(modelo, x_train, y_train)
    guardar_modelo(modelo)
    guardar_tokenizer(tokenizer)

    # Descomenta para probar el chatbot
    # probar_chatbot(modelo, tokenizer)