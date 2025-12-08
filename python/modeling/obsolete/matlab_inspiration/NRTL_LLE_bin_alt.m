function [gamma1,gamma2,gamma3] = NRTL_LLE_bin_alt(kbin,x1,x2,x3)

R = 8.3145; %J/mol K

c = [0 0.2 0.2;
    0.2 0 0.2;
    0.2 0.2 0];

T = 298.15;

x(1,1)=x1;
x(1,2)=x2;
x(1,3)=x3;


dg = [0 kbin(1) kbin(2);
    kbin(3) 0 kbin(4);
    kbin(5) kbin(6) 0];


for i=1:3
    for j=1:3
        tau(i,j) = dg(i,j)/(R*T);
        G(i,j) = exp(-c(i,j)*tau(i,j));
    end
end

for i=1:3
    const1 = 0;
    for j=1:3
        const1 = const1 + x(1,j)*tau(j,i)*G(j,i);
    end
    const2 = 0;
    for k=1:3
        const2= const2 + x(1,k)*G(k,i);
    end
    
    const3 = const1/const2;
    
    const4 = 0;
    
    for j=1:3
               
        const5 = 0;
        
        for k=1:3
            const5 = const5 + x(1,k)*G(k,j);
        end
        
        const6 = 0;
        
        for m=1:3
            const6 = const6 + x(1,m)*tau(m,j)*G(m,j);
        end
        
        const7 = 0;
        
        for k=1:3
            const7 = const7 + x(1,k)*G(k,j);
        end
        
        const8 = const6/const7;
        
        const4 = const4 + (x(1,j)*G(i,j)/const5)*(tau(i,j) - const8);
    end
    
    const9 = const3 + const4;
    
    gamma(1,i) = exp(const9);
end

gamma1 = gamma(1,1);
gamma2 = gamma(1,2);
gamma3 = gamma(1,3);
