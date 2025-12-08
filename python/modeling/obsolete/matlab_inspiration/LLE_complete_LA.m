function kbin = LLE_complete_LA(kbin)
%loop to calculate kbin NRTL vía privat et al. 

x1_final = zeros(5,3);
x2_final = zeros(5,3);

kbin0 = [-100 1 -1 -10000 0 1];
%refino
%1 soluto, 2 carrier, 3 solvente
x1_exp = [0.014	0.872	0.114
0.010	0.869	0.121
0.180	0.716	0.104
0.148	0.764	0.088
0.161	0.758	0.081];
%extracto
%1 soluto, 2 carrier, 3 solvente
x2_exp = [0.008	0.000	0.992
0.018	0.000	0.982
0.062	0.000	0.938
0.097	0.000	0.903
0.145	0.000	0.855];

Settings_fitter = optimset('Display', 'Iter','TolFun',1E-20, 'TolX', 1E-9, 'TolFun', 1E-20,'MaxFunEvals',60000, 'MaxIter',Inf);

[kbin, resnorm, residual, exitflag, output, lamda, jacobian] = lsqnonlin(@nestedsolve, kbin0, [-inf -inf -inf -inf -inf -inf], [inf inf inf inf inf inf], Settings_fitter);
ParametersConfi = nlparci(kbin, residual, jacobian)

    function err = nestedsolve(kbin)
      
     for i=1:5   
        
        [gamma1(i,1),gamma1(i,2),gamma1(i,3)] = NRTL_LLE_bin_alt(kbin,x1_exp(i,1),x1_exp(i,2),x1_exp(i,3));
        [gamma2(i,1),gamma2(i,2),gamma2(i,3)] = NRTL_LLE_bin_alt(kbin,x2_exp(i,1),x2_exp(i,2),x2_exp(i,3));
     
   
        
         A = [gamma1(i,1) 0 -gamma2(i,1) 0
              0 gamma1(i,2) 0 -gamma2(i,2)
              -gamma1(i,3) -gamma1(i,3) gamma2(i,3) gamma2(i,3)
              0 1 0 0]; 
          
          B = [0
              0
              gamma2(i,3)-gamma1(i,3)
              x1_exp(i,2)];
          
          x_n = A\B;
          
          x1_nuevo(i,1) = x_n(1);
          x1_nuevo(i,2) = x_n(2);
          x1_nuevo(i,3) = 1-(x_n(1)+x_n(2));
          
         
          x2_nuevo(i,1) = x_n(3);
          x2_nuevo(i,2) = x_n(4);
          x2_nuevo(i,3) = 1-(x_n(3)+x_n(4));
         %*********************************   
         %nested
          x1_final(i,1) = x_n(1);
          x1_final(i,2) = x_n(2);
          x1_final(i,3) = 1-(x_n(1)+x_n(2));
          
         
          x2_final(i,1) = x_n(3);
          x2_final(i,2) = x_n(4);
          x2_final(i,3) = 1-(x_n(3)+x_n(4));
          %***********************************
          
          error_1(i) = abs(x1_nuevo(i,2) - x1_exp(i,2))^2 + abs(x1_nuevo(i,3) - x1_exp(i,3))^2 + abs(x2_nuevo(i,1) - x2_exp(i,1))^2 + (x2_nuevo(i,3) - x2_exp(i,3))^2;

          
          
     end 
     
     err = sum(error_1);
   
     
      
    end

     xlswrite('data1_LA.xls',x1_final)
     xlswrite('data2_LA.xls',x2_final)

end
