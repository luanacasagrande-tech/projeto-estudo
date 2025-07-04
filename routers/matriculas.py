from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas import Matricula, CursosPorAlunoResponse, AlunosPorCursoResponse
from models import Matricula as ModelMatricula, Aluno as ModelAluno, Curso as ModelCurso # Importe os modelos
from database import get_db

matriculas_router = APIRouter()

@matriculas_router.post("/matriculas", response_model=Matricula, status_code=status.HTTP_201_CREATED)
def create_matricula(matricula: Matricula, db: Session = Depends(get_db)):
    
    db_aluno = db.query(ModelAluno).filter(ModelAluno.id == matricula.aluno_id).first()
    db_curso = db.query(ModelCurso).filter(ModelCurso.id == matricula.curso_id).first()

    if not db_aluno or not db_curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno ou Curso não encontrado")

    # Verifica se a matrícula já existe para evitar duplicatas
    matricula_existente = db.query(ModelMatricula).filter(
        ModelMatricula.aluno_id == matricula.aluno_id,
        ModelMatricula.curso_id == matricula.curso_id
    ).first()
    if matricula_existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Aluno já matriculado neste curso")

    db_matricula = ModelMatricula(**matricula.model_dump())
    db.add(db_matricula)
    db.commit()
    db.refresh(db_matricula)
    return Matricula.model_validate(db_matricula)


@matriculas_router.get("/matriculas", response_model=List[Matricula])
def read_all_matriculas(db: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as matrículas existentes.
    """
    matriculas = db.query(ModelMatricula).all()
    return [Matricula.model_validate(m) for m in matriculas]

@matriculas_router.delete("/matriculas/{matricula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_matricula(matricula_id: int, db: Session = Depends(get_db)):
    """
    Exclui uma matrícula com base no seu ID.
    """
    db_matricula = db.query(ModelMatricula).filter(ModelMatricula.id == matricula_id).first()

    if not db_matricula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula não encontrada")

    db.delete(db_matricula)
    db.commit()
    return

@matriculas_router.get("/matriculas/aluno/{nome_aluno}", response_model=CursosPorAlunoResponse)
def read_matriculas_por_nome_aluno(nome_aluno: str, db: Session = Depends(get_db)):
    db_aluno = db.query(ModelAluno).filter(ModelAluno.nome.ilike(f"%{nome_aluno}%")).first()

    if not db_aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    # Simplifica a busca por nomes de cursos e retorna uma lista vazia se não houver matrículas
    cursos_matriculados = [matricula.curso.nome for matricula in db_aluno.matriculas if matricula.curso]

    return CursosPorAlunoResponse(aluno=db_aluno.nome, cursos=cursos_matriculados)

@matriculas_router.get("/matriculas/curso/{codigo_curso}", response_model=AlunosPorCursoResponse)
def read_alunos_matriculados_por_codigo_curso(codigo_curso: str, db: Session = Depends(get_db)):
    """Retorna o nome do curso e uma lista com os nomes dos alunos matriculados nele."""
    db_curso = db.query(ModelCurso).filter(ModelCurso.codigo == codigo_curso).first()

    if not db_curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")

    # Simplifica a busca por nomes de alunos e retorna uma lista vazia se não houver matrículas
    alunos_matriculados = [matricula.aluno.nome for matricula in db_curso.matriculas if matricula.aluno]

    return AlunosPorCursoResponse(curso=db_curso.nome, alunos=alunos_matriculados)