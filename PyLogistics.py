# Importación de librerías gestion de PDF y uso de fecha y hora actual.
from fpdf import FPDF
from datetime import datetime

# Creación de variables globales.
inventario = []

def agregar_producto():
    """
    Gestiona el flujo de entrada de mercancía al inventario.
    
    Permite dos flujos:
    1. Actualización: Si el nombre ya existe, suma el stock y recalcula la valoración.
    2. Registro: Si es nuevo, solicita datos (precio, importación) y crea el diccionario.
    """

    # Estandarización de entrada para evitar duplicados por formato (ej: "Pino" vs "pino").
    nombre = input("Nombre del producto: ").title().strip()

    # FASE 1: Verificación de existencia previa (Optimización de flujo).
    for producto in inventario:
        if producto["nombre"] == nombre:
            cantidad = input("Cantidad a añadir: ")
            
            # Validación de entrada numérica.
            while not cantidad.isdigit():
                print(f"❌ El valor '{cantidad}' no es un numero válido. Por favor ingrese solo números positivos.")
                cantidad = input("Cantidad a añadir: ")
            
            # Actualización de datos en el diccionario existente.
            producto["cantidad"] += int(cantidad)

            # Recálculo de valoración considerando impuestos por importación (15%).
            factor = 1.15 if producto["es_importado"] else 1
            producto["valor_total"] = round((producto["precio_unitario"] * producto["cantidad"] * factor), 2)
            
            print("✅ Se ha actualizado correctamente la cantidad en inventario")
            return # Finaliza la función si el producto ya fue actualizado.
    
    # FASE 2: Registro de nuevo producto (Si el bucle anterior no encontró coincidencias).

    # Captura y validación de cantidad inicial.
    cantidad = input("Cantidad de unidades: ")
    while not cantidad.isdigit():
        print(f"❌ El valor '{cantidad}' no es un numero válido. Por favor ingrese solo números positivos.")
        cantidad = input("Cantidad de unidades: ")
    cantidad = int(cantidad)

    # Captura de precio con soporte para diferentes formatos de decimales (coma o punto).
    precio_unitario = input("Valor unitario: ")
    while not (precio_unitario.replace(".", "").isdigit() or precio_unitario.replace(",", "").isdigit()):
        print(f"❌ El valor '{precio_unitario}' no es un numero válido. Por favor ingrese solo números positivos.")
        precio_unitario = input("Valor unitario: ")

    precio_unitario = round(float(precio_unitario.replace(",", ".")), 2)

    # Definición de estado tributario (Importación).
    respuesta_es_importado = input("¿Es un producto de importación? (S/N): ")
    while respuesta_es_importado.upper() not in ["S", "N"]:
        print(f"❌ El valor '{respuesta_es_importado}' no es válido. Por favor ingrese solo 'S' para sí, o 'N' para no")
        respuesta_es_importado = input("¿Es un producto de importación? (S/N): ")
    
    # Conversión a Booleano para facilitar cálculos posteriores.
    es_importado = respuesta_es_importado.upper() == "S"

    # Aplicación de regla de negocio: 15% adicional si es importado.
    factor = 1.15 if es_importado else 1
    
    # FASE 3: Consolidación de datos en la estructura del inventario.
    nuevo_item = {
        "nombre" : nombre,
        "cantidad" : cantidad,
        "precio_unitario" : precio_unitario,
        "es_importado" : es_importado,
        "valor_total" : round((precio_unitario * cantidad * factor), 2)
    }

    inventario.append(nuevo_item)
    print(f"✅ '{nombre}' ha sido registrado exitosamente")

def eliminar_producto(producto_eliminar):
    """
    Elimina completamente los datos de un producto, solamente si no hay existencia en stock.
    
    Args:
    producto_eliminar (str): Nombre del producto que se buscará y eliminará.
    """

    # Verificacion de existencia.
    for producto in inventario:

        # Revisión de stock vacío para eliminacion, o mensaje de error.
        if producto["nombre"] == producto_eliminar:

            if producto["cantidad"] == 0:
                print(f"✅ El producto {producto_eliminar} ha sido eliminado del inventario correctamente")
                inventario.remove(producto)
                return

            else:
                print(f"❌ No se puede eliminar {producto_eliminar} porque aún existen {producto["cantidad"]} unidades en el inventario.")
                return

    print(f"❌ El producto {producto_eliminar} no existe en el inventario")

def mostrar_inventario():
    """
    Muestra en pantalla de datos formateados de cada producto existente.

    Expresa mensajes de advertencia cuando un producto tenga poco o nulo stock.
    Añade etiqueta de importación e impuestos adicionales si corresponde.
    """

    # Ciclo de impresion de datos de cada elemento en inventario.
    for producto in inventario:

        print("-" * 30)
        print(f"Producto    :   {producto["nombre"]}    {"[IMPORTADO]" if producto["es_importado"] == True else ""}")
        print(f"Cantidad    :   {producto["cantidad"]}  {"🚨 AGOTADO" if producto["cantidad"] == 0 else "⚠️ REABASTECER PRONTO" if producto["cantidad"] <5 else ""}")
        print(f"Precio Un.  :   ${producto["precio_unitario"]:.2f}")
        print(f"Subtotal    :   ${producto["valor_total"]:.2f}  {"Inc. Impuesto"if producto["es_importado"] == True and producto["valor_total"] != 0 else ""}")
        print("-" * 30)
    

    print(f"VALOR TOTAL DEL INVENTARIO: ${sum([producto["valor_total"] for producto in inventario]):.2f}")

def exportar_reporte_pdf():
    """
    Genera reporte de inventario en formato PDF. 
    
    Se divide en dos secciones:
    1. Tabla de existencia que reporta datos de todos los productos en inventario
    2. Tabla de advertencia que solo exhibe productos con poco o nulo stock. Si no existe poco stock no se genera esta tabla.
    """

    # Verificación de existencia.
    if not inventario:
      print("❌ No existen datos que exportar")  
      return
    
    # Llamado a librería, configuración y automatización de primera página.
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Creación de encabezado de documento, uso de librería 'datetime' para fecha y hora actual.
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 15, "PyLogistics", ln=1, align="C")
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Inventario", ln=1, align="C")
    pdf.set_font("Arial", "", 10)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f"Generado a {fecha}", ln=1, align="C")
    pdf.ln(5)

    # Diccionario para facilicitar la designación de anchos de celda.
    diseño_celdas = {
        "Nombre" : 0.40,
        "Cant." : 0.15,
        "Precio" : 0.20,
        "Subtotal" :0.25
    }
    
    # Encabezado de tabla, uso de diccionario para asignacion de anchos con escalabilidad.
    pdf.set_fill_color(150,150,150)
    pdf.set_font("Arial", "B", 16)
    for celda, porcentaje in diseño_celdas.items():
        salto = 1 if celda == "Subtotal" else 0
        pdf.cell(pdf.epw * porcentaje, 10, celda ,border=1, ln=salto, align="C", fill=True)

    # Inicialización de variables de control para el balance final y alertas de stock.
    total_general = 0
    productos_criticos =[]
    

    # Cuerpo de tabla, uso de diccionario para asignacion de anchos con escalabilidad.
    pdf.set_font("Arial", "", 10)
    for producto in inventario:
        if producto["cantidad"] < 5:                # Adición de producto con bajo stock a lista.
            productos_criticos.append(producto)

        pdf.cell(pdf.epw * diseño_celdas["Nombre"], 10, f"{producto["nombre"]}", border=1, ln=0, align="L")
        pdf.cell(pdf.epw * diseño_celdas["Cant."], 10, f"{producto["cantidad"]}", border=1, ln=0, align="C")
        pdf.cell(pdf.epw * diseño_celdas["Precio"], 10, f"${producto["precio_unitario"]:.2f}", border=1, ln=0, align="C")
        pdf.cell(pdf.epw * diseño_celdas["Subtotal"], 10, f"${producto["valor_total"]:.2f}", border=1, ln=1, align="R")
        total_general += producto["valor_total"]    # Sumatoria de valor general de inventario.
    
    pdf.cell(pdf.epw*0.40 ,10, f"Valor total en inventario:", border=1, ln=0, align="L", fill=True)
    pdf.cell(pdf.epw*0.60 ,10, f"${total_general:.2f}", border=1, ln=1, align="R")


    # Creación de tabla de advertencia si existen productos con bajo stock.
    if productos_criticos:
        pdf.ln(10)
        pdf.set_text_color(200, 0, 0)
        pdf.set_fill_color(255, 228, 230)

        # Encabezado de tabla.
        pdf.cell(0,10,"PRODUCTOS EN RIESGO DE AGOTARSE", border=1, align="C", ln=1, fill=True)
        pdf.cell(pdf.epw * 0.70, 10, "Producto", border=1, align="C", ln=0, fill=True)
        pdf.cell(pdf.epw * 0.30, 10, "Cantidad", border=1, align="C", ln=1, fill=True)

        # Cuerpo de tabla.
        pdf.set_text_color(0, 0, 0)
        for producto in productos_criticos:
            pdf.cell(pdf.epw * 0.70, 10, f"{producto["nombre"]}", border=1, ln=0, align="L")
            pdf.cell(pdf.epw * 0.30, 10, f"{producto["cantidad"]}", border=1, ln=1, align="C")
    
    # Envío de documento generado y salida.
    pdf.output("Informe_inventario.pdf")
    print("✅ Reporte generado con exito")
    return

def menu():
    """
    Muestra menú interactivo al usuario

    Permite 5 opciones:
    1. Añadir productos nuevos o stock a productos existentes.
    2. Mostrar inventario completo.
    3. Eliminar producto sin stock.
    4. Generar reporte de inventario en documento PDF.
    5. Cierre del menú.
    """

    # Apertura de bucle menú.
    while True:
        print("\n" + "="*35)
        print("        SISTEMA PYLOGISTICS        ")
        print("="*35)
        print("1. Registrar Nuevo Producto/Añadir Stock")
        print("2. Consultar Inventario Completo")
        print("3. Eliminar Producto (Seguridad de Stock)")
        print("4. Generar Informe PDF Profesional")
        print("5. Salir del Sistema")
        
        # Captura de valor para determinar la acción.
        opcion = input("\nSeleccione una acción (1-5): ").strip()

        if opcion == "1":
            agregar_producto()
        elif opcion == "2":
            mostrar_inventario()
        elif opcion == "3":
            if not inventario:  # Verificación de existencia
                print("❌ El inventario se encuentra vacío")
            else:
                nombre = input("Nombre del producto a eliminar: ").strip().title() # Captura de valor necesario para funcionamiento de función
                eliminar_producto(nombre)
        elif opcion == "4":
            exportar_reporte_pdf()
        elif opcion == "5":     # Cierre de bucle.
            print("\n👋 Gracias por usar el sistema de PyLogistics ¡Hasta pronto!")
            break
        else:
            print("\n❌ Opción no válida. Por favor, elija un número del 1 al 5.")


menu()