# Pizzerias Maven tiene unos dataset de las pizzas que tienen en el menu, 
# tamaño, pedidos, etc. Como objetivo le gustaria poder saber que stock de 
# ingredientes deberian comprar a la semana, para optimizar el stock de 
# ingredientes y las compras de estos. 

# Importamos las librerias necesarias
import pandas as pd

def contarIngredientes(df, df_ingredientes):
    for i in range(len(df)):
        print("                                                 ", end="\r")
        print(f"\t\tProcesando fila {i+1}/{len(df)}", end="\r")
        ingredientes = df.loc[i, 'ingredients']
        ingredientes = ingredientes.split(",")
        for ingrediente in ingredientes:
            ingrediente = ingrediente.strip()
            if ingrediente in df_ingredientes['ingredient_name'].values:
                df_ingredientes.loc[df_ingredientes['ingredient_name'] == ingrediente, 'cantidad_semanal_necesaria'] += 1
            else:
                data = {'ingredient_name': ingrediente, 'cantidad_semanal_necesaria': 1}
                df_temp = pd.DataFrame.from_dict([data])
                df_ingredientes = pd.concat([df_ingredientes, df_temp])
    return df_ingredientes

def extraer(nombre_archivo):
    df = pd.read_csv(nombre_archivo, encoding = "ISO-8859-1")
    return df

def arreglarDatos(df_orders, df_order_details):
    # Arreglamos los datos corruptos
    df_orders.dropna(inplace=True)
    df_order_details.dropna(inplace=True)

    for i in range(len(df_order_details)):
        pizza = str(df_order_details.loc[i, 'pizza_id'])
        cant = df_order_details.loc[i, 'quantity']
        if pizza == "" or cant == "":
            df_order_details.drop(i, inplace=True)
        if cant == "one" or cant == "One":
            cant = 1
        try:
            for c in pizza:
                if c == "@":
                    pizza = pizza.replace(c, "a")
                elif c == " ":
                    pizza = pizza.replace(c, "_")
                elif c == "-":
                    pizza = pizza.replace(c, "_")
                elif c == "0":
                    pizza = pizza.replace(c, "o")
                elif c == "3":
                    pizza = pizza.replace(c, "e")
        except:
            df_order_details.drop(i, inplace=True)
    return df_orders, df_order_details
            


    return

def transformar(lista_df):
    df_pizzas = lista_df[0]         # Dataframe de pizzas, tamaño y precio
    df_pizza_types = lista_df[1]    # Dataframe de nombre y ingredientes de las pizzas
    df_orders = lista_df[2]         # Dataframe de pedidos y cuandos se hicieron
    df_order_details = lista_df[3]  # Dataframe de que pizzas pidio cada pedido

    # Creamos un nuevo dataframe con todos los datos
    df_orders, df_order_details = arreglarDatos(df_orders, df_order_details)
    df = pd.merge(df_orders, df_order_details, on='order_id')

    df = pd.merge(df, df_pizzas, on='pizza_id')

    df = pd.merge(df, df_pizza_types, on='pizza_type_id')
    df.sort_values(by=['order_details_id'], inplace=True)


    # Creamos un nuevo dataframe con los ingredientes y la cantidad de cada uno por semana
    df_ingredientes = pd.DataFrame(columns=['ingredient_name', 'cantidad_semanal_necesaria'])
    df.reset_index(inplace=True)

    # Calculamos la cantidad de ingredientes
    df_ingredientes = contarIngredientes(df, df_ingredientes)
    
    # Como el año tiene 52 semanas, la cantidad semanal necesaria sera aproximadamente (cantidad total total / 52)
    df_ingredientes['cantidad_semanal_necesaria']= df_ingredientes['cantidad_semanal_necesaria'] // 52

    return df_ingredientes

def etl():

    print(f"\t--> Extrayendo datos...")
    # Primero, extraemos los datos
    df_pizzas = extraer('pizzas.csv')
    df_pizza_types = extraer('pizza_types.csv')
    df_orders = extraer('orders.csv')
    df_order_details = extraer('order_details.csv')

    lista_df = [df_pizzas, df_pizza_types, df_orders, df_order_details]
    print(f"\t    Extraccion terminada.")

    # Segundo, transformamos los datos
    print(f"\t--> Transformando datos...")
    df = transformar(lista_df) 
    print()
    print(f"\t    Transformacion terminada.")
    
    # Tercero, cargamos los datos
    return df



def main():

    print("\n--> Empezando programa. Procesamos los datos con la ETL...")

    # Procesamos los datos mediante una ETL
    try:
        df = etl()
    except:
        print("\nError al leer los datos. Falta algun archivo")
        print("Archivos necesarios:\n\t- pizzas.csv\n\t- pizza_types.csv\n\t- orders.csv\n\t- order_details.csv")
        return


    df.to_csv("ingredientes_semanales.csv")
    print("\n--> Datos procesados. Los datos se han guardado en 'ingredientes_semanales.csv'")
    


    return

if __name__ == '__main__':
    main()