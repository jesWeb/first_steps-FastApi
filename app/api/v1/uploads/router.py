import os
import shutil
import uuid


from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "app/media"
# subir port bytes


@router.post('/bytes')
async def uploads_bytes(file: bytes = File(...)):
    return {
        "filename": "archivo_subido",
        "size_bytes": len(file)
    }


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    if file.content_type not in ['image/png', "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imagenes PNG o JPEG"
        )

    # *extraer la extennsion

    ext = os.path.splitext(file.filename)[1]  # formato .png o .jpeg
    # *crear el nombre
    filename = f"{uuid.uuid4().hex}{ext}"
    # crear el nuevo path
    file_path = os.path.join(MEDIA_DIR, filename)

    """"El buffer es este nuevo archivo que vamos a crear  """""
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "contant_types": file.content_type,
        "url": f"/media/{filename}"
    }
