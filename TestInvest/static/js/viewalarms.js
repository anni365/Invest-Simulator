  function send_low_form() {
    //send_low_form: Envia formulario para dar de baja la alarma.
    document.getElementById("id_id").value = localStorage.id;
    document.getElementById("id_name_low").disabled = false;
    document.getElementById("id_umbral_low").disabled = false;
    document.getElementById("id_price_low").disabled = false;
    alert("Su alarma a sido dada de baja");
    document.getElementById("my_form").submit();
  };
