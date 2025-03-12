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
    # Guardar vocabulario como JSON para compatibilidad
    os.makedirs(os.path.dirname(path), exist_ok=True)
    vocab = tokenizer.get_vocabulary()
    word_index = {word: idx for idx, word in enumerate(vocab)}
    
    # Guardar configuración
    config = tokenizer.get_config()
    
    # Guardar todo en un solo archivo con formato compatible
    tokenizer_data = {
        "config": config,
        "vocabulary": vocab,
        "word_index": word_index
    }
    
    with open(f"{path}.json", 'w', encoding='utf-8') as f:
        json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)
        
    # También guardar en formato pickle para uso directo
    with open(f"{path}.pkl", 'wb') as f:
        pickle.dump(tokenizer, f)
        
    print(f'✅ Tokenizer guardado en {path}.json y {path}.pkl 🚀')

# Probar el chatbot
def probar_chatbot(model, tokenizer):
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() == "salir":
            break
        pregunta_vectorizada = tokenizer([pregunta])
        respuesta = model.predict(pregunta_vectorizada)
        indice = np.argmax(respuesta)
        categorias = ["NEUTRO", "POSITIVO", "NEGATIVO"]
        print("Respuesta: ", categorias[indice])

if __name__ == "__main__":
    archivo_datos = "data/dataset_cleaned.txt"  # Asegúrate de tener un archivo con preguntas y respuestas
    preguntas, respuestas = cargar_datos(archivo_datos)
    x_train, y_train, tokenizer = preprocesar_datos(preguntas, respuestas)
    modelo = construir_modelo(tokenizer)
    entrenar_modelo(modelo, x_train, y_train)
    guardar_modelo(modelo)
    guardar_tokenizer(tokenizer)

    # Descomenta para probar el chatbot
    # probar_chatbot(modelo, tokenizer)
