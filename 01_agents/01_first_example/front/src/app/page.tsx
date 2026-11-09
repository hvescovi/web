"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  api,
  type Celular,
  type CelularInput,
  type Pessoa,
  type PessoaInput,
} from "@/lib/api";
import styles from "./page.module.css";

type Secao = "pessoas" | "celulares";

const pessoaVazia: PessoaInput = { nome: "", email: "", telefone: "" };
const celularVazio: CelularInput = { numero: "", modelo: "", marca: "", pessoa_id: 0 };

export default function Home() {
  const [secao, setSecao] = useState<Secao>("pessoas");
  const [pessoas, setPessoas] = useState<Pessoa[]>([]);
  const [celulares, setCelulares] = useState<Celular[]>([]);
  const [pessoaForm, setPessoaForm] = useState<PessoaInput>(pessoaVazia);
  const [celularForm, setCelularForm] = useState<CelularInput>(celularVazio);
  const [editando, setEditando] = useState<number | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [aviso, setAviso] = useState("");

  const carregarDados = useCallback(async () => {
    try {
      const [listaPessoas, listaCelulares] = await Promise.all([
        api.listPessoas(),
        api.listCelulares(),
      ]);
      setPessoas(listaPessoas);
      setCelulares(listaCelulares);
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Não foi possível carregar os dados.");
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    let active = true;

    async function carregarInicialmente() {
      try {
        const [listaPessoas, listaCelulares] = await Promise.all([
          api.listPessoas(),
          api.listCelulares(),
        ]);
        if (active) {
          setPessoas(listaPessoas);
          setCelulares(listaCelulares);
        }
      } catch (error) {
        if (active) {
          setErro(error instanceof Error ? error.message : "Não foi possível carregar os dados.");
        }
      } finally {
        if (active) setCarregando(false);
      }
    }

    void carregarInicialmente();
    return () => {
      active = false;
    };
  }, []);

  const pessoaPorId = useMemo(
    () => new Map(pessoas.map((pessoa) => [pessoa.id, pessoa.nome])),
    [pessoas],
  );

  function limparFormularios() {
    setEditando(null);
    setPessoaForm(pessoaVazia);
    setCelularForm(celularVazio);
  }

  async function salvarPessoa(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSalvando(true);
    setErro("");
    setAviso("");
    try {
      if (editando === null) {
        await api.createPessoa(pessoaForm);
        setAviso("Pessoa cadastrada com sucesso.");
      } else {
        await api.updatePessoa(editando, pessoaForm);
        setAviso("Pessoa atualizada com sucesso.");
      }
      limparFormularios();
      await carregarDados();
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Não foi possível salvar a pessoa.");
    } finally {
      setSalvando(false);
    }
  }

  async function salvarCelular(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSalvando(true);
    setErro("");
    setAviso("");
    try {
      if (editando === null) {
        await api.createCelular(celularForm);
        setAviso("Celular cadastrado com sucesso.");
      } else {
        await api.updateCelular(editando, celularForm);
        setAviso("Celular atualizado com sucesso.");
      }
      limparFormularios();
      await carregarDados();
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Não foi possível salvar o celular.");
    } finally {
      setSalvando(false);
    }
  }

  function editarPessoa(pessoa: Pessoa) {
    setPessoaForm({
      nome: pessoa.nome,
      email: pessoa.email,
      telefone: pessoa.telefone || "",
    });
    setEditando(pessoa.id);
    setErro("");
    setAviso("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function editarCelular(celular: Celular) {
    setCelularForm({
      numero: celular.numero,
      modelo: celular.modelo,
      marca: celular.marca,
      pessoa_id: celular.pessoa_id,
    });
    setEditando(celular.id);
    setErro("");
    setAviso("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function excluirPessoa(pessoa: Pessoa) {
    if (!window.confirm(`Excluir ${pessoa.nome} e todos os celulares vinculados?`)) return;
    setErro("");
    setAviso("");
    try {
      await api.deletePessoa(pessoa.id);
      setAviso("Pessoa e celulares vinculados excluídos com sucesso.");
      if (editando === pessoa.id) limparFormularios();
      await carregarDados();
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Não foi possível excluir a pessoa.");
    }
  }

  async function excluirCelular(celular: Celular) {
    if (!window.confirm(`Excluir o celular ${celular.numero}?`)) return;
    setErro("");
    setAviso("");
    try {
      await api.deleteCelular(celular.id);
      setAviso("Celular excluído com sucesso.");
      if (editando === celular.id) limparFormularios();
      await carregarDados();
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Não foi possível excluir o celular.");
    }
  }

  const mostrandoPessoas = secao === "pessoas";

  return (
    <main className={styles.page}>
      <header className={styles.topbar}>
        <Link className={styles.brand} href="/" aria-label="Início">
          <span className={styles.brandMark}>+</span>
          <span>cadastro<span className={styles.brandAccent}>.</span></span>
        </Link>
        <span className={styles.topbarLabel}>PAINEL DE GESTÃO</span>
      </header>

      <div className={styles.layout}>
        <aside className={styles.sidebar}>
          <p className={styles.navCaption}>MENU PRINCIPAL</p>
          <button
            className={`${styles.navItem} ${mostrandoPessoas ? styles.navActive : ""}`}
            onClick={() => { setSecao("pessoas"); limparFormularios(); }}
          >
            <span className={styles.navIcon}>◉</span>
            Pessoas
            <span className={styles.navCount}>{pessoas.length}</span>
          </button>
          <button
            className={`${styles.navItem} ${!mostrandoPessoas ? styles.navActive : ""}`}
            onClick={() => { setSecao("celulares"); limparFormularios(); }}
          >
            <span className={styles.navIcon}>▣</span>
            Celulares
            <span className={styles.navCount}>{celulares.length}</span>
          </button>
          <div className={styles.sidebarNote}>
            <span className={styles.statusDot} />
            API conectada
            <small>Banco de dados ativo</small>
          </div>
        </aside>

        <section className={styles.content}>
          <div className={styles.heading}>
            <div>
              <p className={styles.eyebrow}>GERENCIAMENTO</p>
              <h1>{mostrandoPessoas ? "Pessoas" : "Celulares"}</h1>
              <p className={styles.subtitle}>
                {mostrandoPessoas
                  ? "Cadastre e gerencie as pessoas da sua base."
                  : "Gerencie os celulares e seus respectivos proprietários."}
              </p>
            </div>
            <div className={styles.totalCard}>
              <span className={styles.totalIcon}>{mostrandoPessoas ? "◉" : "▣"}</span>
              <div><strong>{mostrandoPessoas ? pessoas.length : celulares.length}</strong><small>registros</small></div>
            </div>
          </div>

          {(erro || aviso) && (
            <div className={`${styles.message} ${erro ? styles.error : styles.success}`} role="status">
              <span>{erro ? "!" : "✓"}</span>
              {erro || aviso}
              <button onClick={() => { setErro(""); setAviso(""); }} aria-label="Fechar mensagem">×</button>
            </div>
          )}

          <div className={styles.workspace}>
            <section className={styles.formCard}>
              <div className={styles.cardHeading}>
                <div>
                  <span className={styles.stepLabel}>{editando === null ? "NOVO REGISTRO" : "EDITANDO REGISTRO"}</span>
                  <h2>{editando === null ? "Adicionar" : "Editar"} {mostrandoPessoas ? "pessoa" : "celular"}</h2>
                </div>
                {editando !== null && (
                  <button className={styles.cancelEdit} onClick={limparFormularios} type="button">Cancelar</button>
                )}
              </div>

              {mostrandoPessoas ? (
                <form onSubmit={salvarPessoa} className={styles.form}>
                  <label>
                    Nome completo <span>*</span>
                    <input
                      required
                      maxLength={120}
                      placeholder="Ex.: Ana Souza"
                      value={pessoaForm.nome}
                      onChange={(event) => setPessoaForm({ ...pessoaForm, nome: event.target.value })}
                    />
                  </label>
                  <label>
                    E-mail <span>*</span>
                    <input
                      required
                      type="email"
                      maxLength={255}
                      placeholder="ana@email.com"
                      value={pessoaForm.email}
                      onChange={(event) => setPessoaForm({ ...pessoaForm, email: event.target.value })}
                    />
                  </label>
                  <label>
                    Telefone <small>(opcional)</small>
                    <input
                      maxLength={40}
                      placeholder="(11) 99999-9999"
                      value={pessoaForm.telefone}
                      onChange={(event) => setPessoaForm({ ...pessoaForm, telefone: event.target.value })}
                    />
                  </label>
                  <button className={styles.submitButton} disabled={salvando} type="submit">
                    <span>{salvando ? "Salvando..." : editando === null ? "＋  Cadastrar pessoa" : "✓  Salvar alterações"}</span>
                  </button>
                </form>
              ) : (
                <form onSubmit={salvarCelular} className={styles.form}>
                  <label>
                    Número <span>*</span>
                    <input
                      required
                      maxLength={40}
                      placeholder="(11) 99999-9999"
                      value={celularForm.numero}
                      onChange={(event) => setCelularForm({ ...celularForm, numero: event.target.value })}
                    />
                  </label>
                  <div className={styles.fieldRow}>
                    <label>
                      Marca <span>*</span>
                      <input
                        required
                        maxLength={80}
                        placeholder="Apple"
                        value={celularForm.marca}
                        onChange={(event) => setCelularForm({ ...celularForm, marca: event.target.value })}
                      />
                    </label>
                    <label>
                      Modelo <span>*</span>
                      <input
                        required
                        maxLength={120}
                        placeholder="iPhone 15"
                        value={celularForm.modelo}
                        onChange={(event) => setCelularForm({ ...celularForm, modelo: event.target.value })}
                      />
                    </label>
                  </div>
                  <label>
                    Pessoa responsável <span>*</span>
                    <select
                      required
                      value={celularForm.pessoa_id || ""}
                      onChange={(event) => setCelularForm({ ...celularForm, pessoa_id: Number(event.target.value) })}
                    >
                      <option value="" disabled>Selecione uma pessoa</option>
                      {pessoas.map((pessoa) => (
                        <option key={pessoa.id} value={pessoa.id}>{pessoa.nome}</option>
                      ))}
                    </select>
                  </label>
                  {pessoas.length === 0 && (
                    <p className={styles.formHint}>Cadastre uma pessoa antes de adicionar um celular.</p>
                  )}
                  <button className={styles.submitButton} disabled={salvando || pessoas.length === 0} type="submit">
                    <span>{salvando ? "Salvando..." : editando === null ? "＋  Cadastrar celular" : "✓  Salvar alterações"}</span>
                  </button>
                </form>
              )}
            </section>

            <section className={styles.listCard}>
              <div className={styles.listHeading}>
                <div>
                  <h2>{mostrandoPessoas ? "Pessoas cadastradas" : "Celulares cadastrados"}</h2>
                  <p>{mostrandoPessoas ? "Todos os registros de pessoas" : "Todos os dispositivos cadastrados"}</p>
                </div>
                <button className={styles.refreshButton} onClick={() => { setErro(""); void carregarDados(); }} aria-label="Atualizar lista">↻</button>
              </div>

              {carregando ? (
                <div className={styles.emptyState}><span className={styles.spinner} />Carregando registros...</div>
              ) : mostrandoPessoas ? (
                pessoas.length === 0 ? (
                  <div className={styles.emptyState}><span className={styles.emptyIcon}>◉</span><strong>Nenhuma pessoa cadastrada</strong><span>Use o formulário para adicionar a primeira pessoa.</span></div>
                ) : (
                  <div className={styles.tableWrap}>
                    <table>
                      <thead><tr><th>PESSOA</th><th>TELEFONE</th><th>CELULARES</th><th className={styles.actionsHeader}>AÇÕES</th></tr></thead>
                      <tbody>
                        {pessoas.map((pessoa) => {
                          const totalCelulares = celulares.filter((celular) => celular.pessoa_id === pessoa.id).length;
                          return (
                            <tr key={pessoa.id}>
                              <td>
                                <div className={styles.personCell}>
                                  <span className={styles.avatar}>{pessoa.nome.trim().charAt(0).toUpperCase()}</span>
                                  <span><strong>{pessoa.nome}</strong><small>{pessoa.email}</small></span>
                                </div>
                              </td>
                              <td>{pessoa.telefone || <span className={styles.muted}>—</span>}</td>
                              <td><span className={styles.badge}>{totalCelulares} {totalCelulares === 1 ? "celular" : "celulares"}</span></td>
                              <td><div className={styles.actions}>
                                <button onClick={() => editarPessoa(pessoa)} aria-label={`Editar ${pessoa.nome}`}>Editar</button>
                                <button className={styles.deleteAction} onClick={() => void excluirPessoa(pessoa)} aria-label={`Excluir ${pessoa.nome}`}>Excluir</button>
                              </div></td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )
              ) : celulares.length === 0 ? (
                <div className={styles.emptyState}><span className={styles.emptyIcon}>▣</span><strong>Nenhum celular cadastrado</strong><span>Use o formulário para adicionar o primeiro celular.</span></div>
              ) : (
                <div className={styles.tableWrap}>
                  <table>
                    <thead><tr><th>DISPOSITIVO</th><th>NÚMERO</th><th>PESSOA</th><th className={styles.actionsHeader}>AÇÕES</th></tr></thead>
                    <tbody>
                      {celulares.map((celular) => (
                        <tr key={celular.id}>
                          <td><div className={styles.deviceCell}><span className={styles.deviceIcon}>▣</span><span><strong>{celular.marca}</strong><small>{celular.modelo}</small></span></div></td>
                          <td>{celular.numero}</td>
                          <td><span className={styles.personTag}>{pessoaPorId.get(celular.pessoa_id) || celular.pessoa_nome}</span></td>
                          <td><div className={styles.actions}>
                            <button onClick={() => editarCelular(celular)} aria-label={`Editar celular ${celular.numero}`}>Editar</button>
                            <button className={styles.deleteAction} onClick={() => void excluirCelular(celular)} aria-label={`Excluir celular ${celular.numero}`}>Excluir</button>
                          </div></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className={styles.listFooter}>
                Exibindo <strong>{mostrandoPessoas ? pessoas.length : celulares.length}</strong> {mostrandoPessoas ? "pessoas" : "celulares"}
              </div>
            </section>
          </div>
          <footer className={styles.footer}>Cadastro<span>.</span> <small>Gestão simples, organizada e eficiente.</small></footer>
        </section>
      </div>
    </main>
  );
}
