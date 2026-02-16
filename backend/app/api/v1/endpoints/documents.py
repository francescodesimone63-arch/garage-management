"""
API endpoints per la gestione dei documenti (Documents).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.document import Document, DocumentType
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentWithDetails
)

router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    document_type: Optional[DocumentType] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera documenti con filtri.
    """
    query = db.query(Document)
    
    # Filtro tipo documento
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Filtro entità associata
    if entity_type:
        query = query.filter(Document.entity_type == entity_type)
    if entity_id:
        query = query.filter(Document.entity_id == entity_id)
    
    query = query.order_by(Document.uploaded_at.desc())
    documents = query.offset(skip).limit(limit).all()
    
    return documents


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea nuovo record documento (metadati).
    Upload file separato con endpoint /upload.
    """
    # Crea documento
    document = Document(**document_data.model_dump(), uploaded_by_id=current_user.id)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document


@router.post("/{document_id}/upload", response_model=dict)
async def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload file fisico per documento.
    
    TODO: Implementare storage (locale, S3, etc.)
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento ID {document_id} non trovato"
        )
    
    # TODO: Salvare file su storage
    # - Validare tipo file
    # - Generare nome file unico
    # - Salvare su filesystem o cloud storage
    # - Aggiornare document.file_path e document.file_size
    
    # Placeholder
    file_size = 0
    try:
        content = await file.read()
        file_size = len(content)
        # Qui salveresti il file
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore upload file: {str(e)}"
        )
    
    # Aggiorna metadati documento
    document.file_name = file.filename
    document.file_size = file_size
    document.mime_type = file.content_type
    # document.file_path = f"/storage/documents/{document_id}/{file.filename}"
    
    db.commit()
    
    return {
        "success": True,
        "document_id": document_id,
        "file_name": file.filename,
        "file_size": file_size,
        "message": "File upload placeholder - implementare storage reale"
    }


@router.get("/{document_id}", response_model=DocumentWithDetails)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli documento.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento ID {document_id} non trovato"
        )
    
    # Info uploader
    uploader_info = None
    if document.uploaded_by:
        uploader_info = {
            "id": document.uploaded_by.id,
            "full_name": document.uploaded_by.full_name,
            "email": document.uploaded_by.email
        }
    
    return DocumentWithDetails(
        **document.__dict__,
        uploader_info=uploader_info
    )


@router.get("/{document_id}/download", response_model=dict)
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download file documento.
    
    TODO: Implementare download da storage.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento ID {document_id} non trovato"
        )
    
    if not document.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File non trovato per questo documento"
        )
    
    # TODO: Restituire FileResponse con file da storage
    # from fastapi.responses import FileResponse
    # return FileResponse(
    #     path=document.file_path,
    #     filename=document.file_name,
    #     media_type=document.mime_type
    # )
    
    return {
        "document_id": document_id,
        "file_name": document.file_name,
        "file_path": document.file_path,
        "message": "Download placeholder - implementare storage reale"
    }


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna metadati documento.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento ID {document_id} non trovato"
        )
    
    # Verifica permessi (uploader o admin)
    if document.uploaded_by_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.GENERAL_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a modificare questo documento"
        )
    
    # Aggiorna campi
    update_data = document_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina documento.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento ID {document_id} non trovato"
        )
    
    # Verifica permessi
    if document.uploaded_by_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.GENERAL_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a eliminare questo documento"
        )
    
    # TODO: Eliminare file fisico da storage
    # if document.file_path:
    #     os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return None


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[DocumentResponse])
def get_entity_documents(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera tutti i documenti associati a un'entità specifica.
    
    entity_type: 'customer', 'vehicle', 'work_order', etc.
    """
    documents = db.query(Document).filter(
        and_(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id
        )
    ).order_by(Document.uploaded_at.desc()).all()
    
    return documents


@router.get("/stats/summary", response_model=dict)
def get_document_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiche documenti.
    """
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    
    # Conta per tipo
    type_stats = db.query(
        Document.document_type,
        func.count(Document.id)
    ).group_by(Document.document_type).all()
    
    # Spazio totale occupato
    total_size = db.query(func.sum(Document.file_size)).scalar() or 0
    total_size_mb = round(total_size / (1024 * 1024), 2)
    
    # Conta per entità
    entity_stats = db.query(
        Document.entity_type,
        func.count(Document.id)
    ).group_by(Document.entity_type).all()
    
    return {
        "total_documents": total_documents,
        "total_size_mb": total_size_mb,
        "by_type": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in type_stats
        },
        "by_entity": {
            stat[0] if stat[0] else "unknown": stat[1]
            for stat in entity_stats
        }
    }
