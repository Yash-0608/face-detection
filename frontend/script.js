const input =
document.getElementById(
    "imageInput"
);



input.onchange = () => {


    const file =
    input.files[0];


    document.getElementById(
        "preview"
    ).src =
    URL.createObjectURL(file);


};



async function detectFace(){


    const file =
    input.files[0];


    if(!file){

        alert(
            "Please select image"
        );

        return;

    }



    const formData =
    new FormData();



    formData.append(
        "image",
        file
    );



    const response =
    await fetch(

        "/detect",

        {

            method:"POST",

            body:formData

        }

    );



    const data =
    await response.json();



    document.getElementById(
        "result"
    ).src =
    data.result;


}