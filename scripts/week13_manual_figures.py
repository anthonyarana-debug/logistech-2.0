# Figure geometry is calibrated against each original screenshot at 324 × 225.
# Rectangle origin, dimensions, and the instruction it supports.
FIGURES = {
    1: [
        (247, 5, 16, 12, "action", "Abre Sign in para iniciar sesión."),
        (266, 4, 41, 13, "action", "Abre Create account para solicitar una cuenta."),
    ],
    2: [
        (187, 69, 95, 13, "field", "Completa First name."),
        (187, 91, 95, 13, "field", "Escribe Email address."),
        (187, 112, 82, 15, "field", "Introduce Password."),
        (
            271,
            112,
            12,
            15,
            "action",
            "Usa el ojo para comprobar la contraseña en privado.",
        ),
        (187, 144, 95, 14, "field", "Repite la contraseña en Confirm password."),
        (187, 162, 95, 15, "action", "Pulsa Create operator account."),
    ],
    3: [(186, 68, 98, 16, "warning", "Completa el campo obligatorio resaltado.")],
    4: [
        (
            186,
            62,
            98,
            26,
            "error",
            "Corrige los dos valores de contraseña y vuelve a enviar.",
        )
    ],
    5: [(186, 115, 39, 15, "action", "Pulsa Sign in para volver al acceso.")],
    6: [
        (186, 90, 97, 15, "field", "Introduce el correo de la cuenta."),
        (186, 112, 97, 15, "field", "Introduce su contraseña."),
        (186, 129, 97, 16, "action", "Pulsa Sign in."),
    ],
    7: [
        (186, 71, 98, 26, "error", "Revisa las credenciales y vuelve a iniciar sesión.")
    ],
    8: [(146, 80, 32, 15, "action", "Pulsa Sign in again y autentícate de nuevo.")],
    9: [(57, 129, 50, 16, "action", "Vuelve al espacio de trabajo desde el botón.")],
    10: [
        (
            57,
            129,
            50,
            16,
            "action",
            "Vuelve al espacio de trabajo y usa una cuenta autorizada.",
        )
    ],
    11: [
        (2, 32, 47, 113, "field", "Elige el módulo en el menú lateral."),
        (247, 25, 68, 15, "field", "Selecciona el ámbito de empresa."),
    ],
    12: [
        (66, 90, 199, 16, "field", "Filtra por nombre o estado."),
        (279, 56, 38, 15, "action", "Abre Create company."),
    ],
    13: [
        (95, 95, 133, 37, "field", "Completa el nombre y el estado de la empresa."),
        (194, 141, 34, 16, "action", "Pulsa Save changes."),
    ],
    14: [
        (65, 92, 176, 15, "field", "Busca una sucursal."),
        (282, 56, 35, 15, "action", "Pulsa Create branch."),
    ],
    15: [
        (95, 72, 133, 82, "field", "Completa empresa, nombre, dirección y estado."),
        (194, 161, 34, 16, "action", "Pulsa Save changes."),
    ],
    16: [
        (65, 92, 175, 15, "field", "Busca por nombre o SKU."),
        (282, 56, 35, 15, "action", "Pulsa Create product."),
    ],
    17: [
        (
            95,
            52,
            133,
            117,
            "field",
            "Completa empresa, producto, SKU, categoría y estado.",
        ),
        (194, 178, 34, 16, "action", "Pulsa Save changes."),
    ],
    18: [
        (65, 92, 124, 15, "field", "Busca al usuario por nombre o correo."),
        (285, 56, 33, 15, "action", "Pulsa Create user."),
    ],
    19: [
        (
            95,
            27,
            133,
            150,
            "field",
            "Completa correo, nombre, rol y asignaciones permitidas.",
        ),
        (194, 209, 34, 14, "action", "Pulsa Save changes."),
    ],
    20: [
        (64, 91, 224, 16, "field", "Filtra por texto o condición."),
        (273, 57, 44, 15, "action", "Pulsa Create category."),
    ],
    21: [
        (94, 74, 133, 85, "field", "Escribe el nombre y revisa las condiciones."),
        (193, 172, 34, 15, "action", "Pulsa Save category."),
    ],
    22: [
        (64, 93, 224, 17, "field", "Aplica filtros y comprueba el resultado."),
        (279, 58, 38, 15, "action", "Pulsa Register box para dar de alta una caja."),
    ],
    23: [
        (95, 64, 133, 90, "field", "Elige producto, sucursal y cantidad."),
        (200, 177, 28, 15, "action", "Pulsa Save box."),
    ],
    24: [(232, 201, 88, 15, "action", "Comprueba el aviso de caja registrada.")],
    25: [(68, 162, 48, 47, "field", "Consulta el QR de la caja en su detalle.")],
    26: [
        (67, 96, 108, 18, "field", "Introduce el código o el identificador interno."),
        (66, 115, 29, 15, "action", "Pulsa Find box."),
        (
            188,
            112,
            37,
            15,
            "action",
            "Usa Start camera si el navegador concede acceso.",
        ),
    ],
    27: [
        (192, 120, 119, 17, "field", "Selecciona Received para aceptar."),
        (191, 143, 44, 15, "action", "Pulsa Record reception."),
    ],
    28: [
        (191, 138, 120, 15, "warning", "Elige un motivo antes de guardar un rechazo.")
    ],
    29: [
        (
            60,
            134,
            253,
            32,
            "action",
            "Comprueba que la recepción aparece en los registros.",
        )
    ],
    30: [(59, 90, 256, 18, "field", "Filtra por caja y revisa los eventos.")],
    31: [
        (
            185,
            132,
            99,
            18,
            "action",
            "Comprueba que al salir se muestra de nuevo el acceso.",
        )
    ],
    32: [(278, 62, 40, 15, "action", "Abre Boxes desde el espacio de operador.")],
    33: [
        (
            131,
            108,
            43,
            15,
            "action",
            "Pulsa Check assignment cuando el administrador confirme la asignación.",
        )
    ],
    34: [
        (
            81,
            104,
            38,
            16,
            "action",
            "Pulsa Check service para consultar la API y PostgreSQL.",
        )
    ],
    35: [
        (65, 123, 53, 15, "action", "Pulsa Download printable label."),
        (
            218,
            177,
            76,
            17,
            "warning",
            "Verifica el estado antes de registrar una transición.",
        ),
    ],
    36: [(62, 132, 250, 48, "action", "Verifica la recepción guardada en la tabla.")],
    37: [(61, 111, 250, 55, "field", "Contrasta los eventos de creación y recepción.")],
}
