import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

class NRTL:
    def __init__(self, tau12, tau21, alpha12):
        self.tau12 = tau12
        self.tau21 = tau21
        self.alpha12 = alpha12
        
    def gammas(self, x1, T=298):
        """Calcula coeficientes de actividad para sistema binario"""
        x2 = 1 - x1
        
        # Evitar divisiones por cero
        if x1 == 0 or x2 == 0:
            return [1.0, 1.0]
        
        # Prevenir errores numéricos
        alpha = max(0.01, min(self.alpha12, 0.5))
        
        G12 = np.exp(-alpha * self.tau12)
        G21 = np.exp(-alpha * self.tau21)
        
        # Cálculo de coeficientes
        term1 = self.tau21 * (G21/(x1 + x2*G21))**2
        term2 = self.tau12 * G12/(x2 + x1*G12)**2
        ln_gamma1 = x2**2 * (term1 + term2)
        
        term3 = self.tau12 * (G12/(x2 + x1*G12))**2
        term4 = self.tau21 * G21/(x1 + x2*G21)**2
        ln_gamma2 = x1**2 * (term3 + term4)
        
        return [np.exp(ln_gamma1), np.exp(ln_gamma2)]

def nrtl_model(x, tau12, tau21, alpha12):
    model = NRTL(tau12, tau21, alpha12)
    return [model.gammas(xi)[0] for xi in x]

def get_manual_parameters():
    """Solicita parámetros iniciales al usuario con validación"""
    print("\n" + "="*50)
    print("INGRESO MANUAL DE PARÁMETROS INICIALES")
    print("="*50)
    
    while True:
        try:
            tau12 = float(input("Valor inicial para τ12: ").strip() or 0.5)
            tau21 = float(input("Valor inicial para τ21: ").strip() or 0.5)
            alpha12 = float(input("Valor inicial para α12: ").strip() or 0.3)
            
            # Validar rango de alpha
            if not (0.01 <= alpha12 <= 0.5):
                print("¡ADVERTENCIA! α12 debe estar entre 0.01 y 0.5")
                if input("¿Forzar valor? (s/n): ").lower() != 's':
                    continue
            
            return [tau12, tau21, alpha12]
        
        except ValueError:
            print("Error: Ingrese valores numéricos válidos")
            continue

# ===================================================================
# PROGRAMA PRINCIPAL
# ===================================================================
if __name__ == "__main__":
    # Configuración de datos
    # (Reemplazar con tus datos reales del ESP32)
    x_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    gamma_data = np.array([2.5, 2.0, 1.6, 1.3, 1.1, 1.3, 1.6, 2.0, 2.5])  # Ejemplo en forma de U
    
    print("DATOS EXPERIMENTALES:")
    print(f"Fracciones molares: {x_data}")
    print(f"Coeficientes de actividad: {gamma_data}")
    
    # Menú principal
    while True:
        print("\n" + "="*50)
        print("MENÚ PRINCIPAL - MODELADO NRTL")
        print("="*50)
        print("1. Ingresar parámetros iniciales manualmente")
        print("2. Usar valores por defecto [0.5, 0.5, 0.3]")
        print("3. Ver gráfico de datos experimentales")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            p0 = get_manual_parameters()
        elif opcion == '2':
            p0 = [0.5, 0.5, 0.3]
            print("\nUsando valores por defecto:")
            print(f"τ12 = {p0[0]}, τ21 = {p0[1]}, α12 = {p0[2]}")
        elif opcion == '3':
            plt.figure(figsize=(10, 6))
            plt.scatter(x_data, gamma_data, color='red', s=80)
            plt.title('Datos Experimentales del ESP32', fontsize=14)
            plt.xlabel('Fracción Molar $x_1$', fontsize=12)
            plt.ylabel('$\\gamma_1$', fontsize=12)
            plt.grid(True)
            plt.savefig()    #guarda la imagen del grafico
            continue
        elif opcion == '4':
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")
            continue
        
        # Intentar ajuste con parámetros seleccionados
        try:
            print("\nIniciando ajuste de parámetros...")
            params, _ = curve_fit(
                nrtl_model, 
                x_data, 
                gamma_data, 
                p0=p0,
                bounds=([-10, -10, 0.01], [10, 10, 0.5]),
                maxfev=5000
            )
            
            tau12_opt, tau21_opt, alpha12_opt = params
            print("\n" + "="*50)
            print("RESULTADOS DEL AJUSTE")
            print("="*50)
            print(f"Parámetros iniciales: τ12={p0[0]:.4f}, τ21={p0[1]:.4f}, α12={p0[2]:.4f}")
            print(f"Parámetros optimizados: τ12={tau12_opt:.4f}, τ21={tau21_opt:.4f}, α12={alpha12_opt:.4f}")
            
            # Validación y gráfico
            model = NRTL(tau12_opt, tau21_opt, alpha12_opt)
            x_test = np.linspace(0.01, 0.99, 100)
            gamma_pred = [model.gammas(xi)[0] for xi in x_test]
            
            # Cálculo del error
            gamma_calc = nrtl_model(x_data, tau12_opt, tau21_opt, alpha12_opt)
            error = np.mean(np.abs(gamma_data - gamma_calc))
            print(f"Error medio absoluto: {error:.6f}")
            
            # Gráfico comparativo
            plt.figure(figsize=(10, 6))
            plt.scatter(x_data, gamma_data, color='red', s=80, label='Datos')
            plt.plot(x_test, gamma_pred, 'b-', lw=2, label=f'Modelo NRTL (α={alpha12_opt:.4f})')
            plt.title('Ajuste del Modelo NRTL', fontsize=14)
            plt.xlabel('Fracción Molar $x_1$', fontsize=12)
            plt.ylabel('$\\gamma_1$', fontsize=12) 
            plt.legend()
            plt.grid(True)
            plt.savefig('resultados_nrtl.png', dpi=300)
            
            # Guardar resultados en archivo
            with open('parametros_optimizados.txt', 'w') as f:
                f.write("Parámetros optimizados NRTL\n")
                f.write("=========================\n")
                f.write(f"τ12 = {tau12_opt:.6f}\n")
                f.write(f"τ21 = {tau21_opt:.6f}\n")
                f.write(f"α12 = {alpha12_opt:.6f}\n")
                f.write(f"Error medio absoluto = {error:.6f}\n")
            
            print("Resultados guardados en 'parametros_optimizados.txt'")
            
        except Exception as e:
            print(f"\nERROR EN EL AJUSTE: {str(e)}")
            print("Posibles soluciones:")
            print("1. Verificar la calidad de los datos")
            print("2. Probar diferentes valores iniciales")
            print("3. Aumentar maxfev en el código (actual maxfev=5000)")
            
        # Preguntar si desea continuar
        if input("\n¿Desea realizar otro ajuste? (s/n): ").lower() != 's':
            print("Saliendo del programa...")
            break