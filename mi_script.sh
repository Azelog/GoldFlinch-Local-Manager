a = true
while $a; do	
	opcion=$(kdialog --menu "Elige una opción" \
    	1 "Ejecutar script A" \
    	2 "Ejecutar script B" \
    	3 "Salir")
	case $opcion in
        	1) echo "A" ;;
        	2) echo "B" ;;
	        *) echo "Cancelado"; a=false ;;
	esac
done
