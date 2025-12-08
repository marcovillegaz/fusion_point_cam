import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize
from scipy.interpolate import make_interp_spline

class NRTLPhaseModel:
    """
    Modelo para diagramas de fase líquido-sólido usando NRTL
    """
    def __init__(self, g12, g21, alpha12):
        self.g12 = g12  # Parámetro de energía [J/mol]
        self.g21 = g21  # Parámetro de energía [J/mol]
        self.alpha12 = alpha12  # Parámetro de no-aleatoriedad
        self.R = 8.314  # Constante de los gases [J/(mol·K)]
    
    def activity_coeffs(self, x1, T):
        """Calcula coeficientes de actividad"""
        x2 = 1 - x1
        
        # Convertir a parámetros τ (adimensionales)
        tau12 = self.g12 / (self.R * T)
        tau21 = self.g21 / (self.R * T)
        
        # Prevenir errores numéricos
        alpha = max(0.01, min(self.alpha12, 0.5))
        
        # Cálculo de parámetros G
        G12 = np.exp(-alpha * tau12)
        G21 = np.exp(-alpha * tau21)
        
        # Coeficiente de actividad componente 1
        ln_gamma1 = x2**2 * (
            tau21 * (G21/(x1 + x2*G21))**2 + 
            (tau12 * G12)/(x2 + x1*G12)**2
        )
        
        # Coeficiente de actividad componente 2
        ln_gamma2 = x1**2 * (
            tau12 * (G12/(x2 + x1*G12))**2 + 
            (tau21 * G21)/(x1 + x2*G21)**2
        )
        
        return [np.exp(ln_gamma1), np.exp(ln_gamma2)]
    
    def liquidus_temperature(self, x1, T_fus1, DH_fus1, T_fus2, DH_fus2):
        """
        Calcula la temperatura de líquidus para una composición dada
        utilizando el método de punto fijo
        """
        # Valor inicial de temperatura (promedio de los puntos de fusión)
        T = (T_fus1 + T_fus2) / 2
        
        # Iterar hasta convergencia
        for _ in range(50):
            gamma1, gamma2 = self.activity_coeffs(x1, T)
            
            # Calcular temperatura para ambos componentes
            T1 = 1 / (1/T_fus1 - (self.R * np.log(gamma1 * x1)) / DH_fus1)
            T2 = 1 / (1/T_fus2 - (self.R * np.log(gamma2 * (1 - x1))) / DH_fus2)
            
            # Tomar la temperatura más baja (conservadora)
            T_new = min(T1, T2) if not np.isnan(T1) and not np.isnan(T2) else T
            
            # Comprobar convergencia
            if abs(T_new - T) < 0.01:
                return T_new
            T = T_new
        
        return T

def nrtl_liquidus_model(x, g12, g21, alpha12, T_fus1, DH_fus1, T_fus2, DH_fus2):
    """Función para ajuste de parámetros a datos de líquidus"""
    model = NRTLPhaseModel(g12, g21, alpha12)
    return [model.liquidus_temperature(xi, T_fus1, DH_fus1, T_fus2, DH_fus2) for xi in x]

def main():
    print("="*70)
    print("MODELADO TERMODINÁMICO DE DIAGRAMAS DE FASE")
    print("="*70)
    print("Configuración de componentes puros:")
    
    # Propiedades de los componentes (ejemplo genérico)
    comp1_name = input("Nombre componente 1 (ej. Solvente): ") or "Solvente"
    T_fus1 = float(input(f"Temperatura de fusión {comp1_name} [K] (default=350): ") or 350)
    DH_fus1 = float(input(f"Entalpía de fusión {comp1_name} [kJ/mol] (default=15): ") or 15) * 1000
    
    comp2_name = input("\nNombre componente 2 (ej. Soluto): ") or "Soluto"
    T_fus2 = float(input(f"Temperatura de fusión {comp2_name} [K] (default=400): ") or 400)
    DH_fus2 = float(input(f"Entalpía de fusión {comp2_name} [kJ/mol] (default=20): ") or 20) * 1000
    
    print("\n" + "="*70)
    print("Parámetros NRTL iniciales:")
    g12 = float(input("Parámetro g12 [J/mol] (default=-2000): ") or -2000)
    g21 = float(input("Parámetro g21 [J/mol] (default=-3000): ") or -3000)
    alpha = float(input("Parámetro alpha (default=0.3): ") or 0.3)
    
    print("\n" + "="*70)
    print("Datos experimentales (Temperatura de líquidus):")
    print("Ingrese fracciones molares del componente 1 y temperaturas correspondientes")
    print("Ejemplo: 0.1,320; 0.3,310; 0.5,300; 0.7,310; 0.9,320")
    data_input = input("Datos [x1,T] separados por punto y coma: ")
    
    # Procesar datos experimentales
    x_data = []
    T_data = []
    for pair in data_input.split(';'):
        try:
            x, T = pair.split(',')
            x_data.append(float(x.strip()))
            T_data.append(float(T.strip()))
        except:
            continue
    
    x_data = np.array(x_data)
    T_data = np.array(T_data)
    
    # Ordenar por fracción molar
    sort_idx = np.argsort(x_data)
    x_data = x_data[sort_idx]
    T_data = T_data[sort_idx]
    
    # Ajuste de parámetros
    print("\nAjustando parámetros NRTL a datos experimentales...")
    try:
        params, _ = curve_fit(
            lambda x, g12, g21, alpha: nrtl_liquidus_model(
                x, g12, g21, alpha, T_fus1, DH_fus1, T_fus2, DH_fus2
            ),
            x_data, 
            T_data, 
            p0=[g12, g21, alpha],
            bounds=([-10000, -10000, 0.1], [0, 0, 0.5]),
            maxfev=5000
        )
        g12_opt, g21_opt, alpha_opt = params
        print("¡Ajuste exitoso!")
        print(f"Parámetros optimizados: g12={g12_opt:.1f} J/mol, g21={g21_opt:.1f} J/mol, alpha={alpha_opt:.4f}")
    except Exception as e:
        print(f"Error en ajuste: {str(e)}")
        print("Usando parámetros iniciales para la visualización")
        g12_opt, g21_opt, alpha_opt = g12, g21, alpha
    
    # Crear modelo con parámetros optimizados
    model = NRTLPhaseModel(g12_opt, g21_opt, alpha_opt)
    
    # Calcular curva teórica
    x_test = np.linspace(0.01, 0.99, 50)
    T_pred = [model.liquidus_temperature(x, T_fus1, DH_fus1, T_fus2, DH_fus2) for x in x_test]
    
    # Suavizar curva para mejor visualización
    if len(x_test) > 3:
        spline = make_interp_spline(x_test, T_pred, k=3)
        x_smooth = np.linspace(0.01, 0.99, 100)
        T_smooth = spline(x_smooth)
    else:
        x_smooth, T_smooth = x_test, T_pred
    
    # Encontrar punto eutéctico aproximado
    eutectic_idx = np.argmin(T_pred)
    x_eutectic = x_test[eutectic_idx]
    T_eutectic = T_pred[eutectic_idx]
    
    # =========================================================================
    # VISUALIZACIÓN DEL DIAGRAMA DE FASE
    # =========================================================================
    plt.figure(figsize=(10, 7))
    
    # Curva teórica
    plt.plot(x_smooth, T_smooth, 'b-', lw=2.5, label='Modelo NRTL')
    
    # Puntos experimentales
    plt.plot(x_data, T_data, 'ro', markersize=8, markerfacecolor='none', 
             markeredgewidth=2, label='Datos Experimentales')
    
    # Punto eutéctico
    plt.plot(x_eutectic, T_eutectic, 'g*', markersize=15, 
             label=f'Eutéctico (~{x_eutectic:.2f}, {T_eutectic:.1f} K)')
    
    # Líneas de componentes puros
    plt.axhline(y=T_fus1, color='purple', linestyle='--', alpha=0.7, 
                label=f'Fusión {comp1_name} ({T_fus1} K)')
    plt.axhline(y=T_fus2, color='orange', linestyle='--', alpha=0.7, 
                label=f'Fusión {comp2_name} ({T_fus2} K)')
    
    # Configuración del gráfico
    plt.title('Diagrama de Fase: Temperatura vs Fracción Molar', fontsize=16)
    plt.xlabel(f'Fracción Molar de {comp1_name}', fontsize=14)
    plt.ylabel('Temperatura (K)', fontsize=14)
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlim(0, 1)
    plt.ylim(min(T_data.min(), T_eutectic) - 10, max(T_fus1, T_fus2) + 10)
    
    # Información termodinámica
    plt.text(0.05, 0.95, 
             f'$g_{{12}}$ = {g12_opt:.1f} J/mol\n$g_{{21}}$ = {g21_opt:.1f} J/mol\n$\\alpha$ = {alpha_opt:.3f}',
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('diagrama_fase_nrtl.png', dpi=300)
    plt.show()
    
    # =========================================================================
    # RESULTADOS TERMODINÁMICOS
    # =========================================================================
    print("\n" + "="*70)
    print("RESULTADOS TERMODINÁMICOS")
    print("="*70)
    print(f"Punto eutéctico estimado: x = {x_eutectic:.3f}, T = {T_eutectic:.1f} K")
    print(f"Depresión del punto de fusión: {max(T_fus1, T_fus2) - T_eutectic:.1f} K")
    
    # Calcular coeficientes de actividad en el eutéctico
    gamma1, gamma2 = model.activity_coeffs(x_eutectic, T_eutectic)
    print(f"\nCoeficientes de actividad en el eutéctico:")
    print(f"{comp1_name}: γ₁ = {gamma1:.3f}")
    print(f"{comp2_name}: γ₂ = {gamma2:.3f}")
    
    # Evaluar no idealidad
    print("\nEvaluación de no idealidad:")
    if abs(gamma1 - 1) > 0.2 or abs(gamma2 - 1) > 0.2:
        print("- Sistema significativamente no ideal (γ ≠ 1)")
    if T_eutectic < min(T_fus1, T_fus2) - 50:
        print("- Fuerte depresión del punto de fusión (característica DES)")

if __name__ == "__main__":
    main()