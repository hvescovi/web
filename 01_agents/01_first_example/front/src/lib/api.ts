export type Pessoa = {
  id: number;
  nome: string;
  email: string;
  telefone: string | null;
};

export type Celular = {
  id: number;
  numero: string;
  modelo: string;
  marca: string;
  pessoa_id: number;
  pessoa_nome: string;
};

export type PessoaInput = {
  nome: string;
  email: string;
  telefone: string;
};

export type CelularInput = {
  numero: string;
  modelo: string;
  marca: string;
  pessoa_id: number;
};

type ApiResponse<T> = {
  resultado: "ok" | "erro";
  detalhes: T | string;
};

const apiUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000").replace(
  /\/+$/,
  "",
);

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiUrl}${path}`, {
      ...init,
      headers: {
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new Error("Não foi possível conectar à API. Verifique se o backend está em execução.");
  }

  const payload = (await response.json().catch(() => null)) as ApiResponse<T> | null;
  if (!response.ok || !payload || payload.resultado !== "ok") {
    const message =
      typeof payload?.detalhes === "string"
        ? payload.detalhes
        : "Não foi possível concluir a operação.";
    throw new Error(message);
  }
  return payload.detalhes as T;
}

export const api = {
  listPessoas: () => request<Pessoa[]>("/pessoas"),
  createPessoa: (data: PessoaInput) =>
    request<Pessoa>("/pessoas", { method: "POST", body: JSON.stringify(data) }),
  updatePessoa: (id: number, data: PessoaInput) =>
    request<Pessoa>(`/pessoas/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deletePessoa: (id: number) =>
    request<{ mensagem: string }>(`/pessoas/${id}`, { method: "DELETE" }),
  listCelulares: () => request<Celular[]>("/celulares"),
  createCelular: (data: CelularInput) =>
    request<Celular>("/celulares", { method: "POST", body: JSON.stringify(data) }),
  updateCelular: (id: number, data: CelularInput) =>
    request<Celular>(`/celulares/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteCelular: (id: number) =>
    request<{ mensagem: string }>(`/celulares/${id}`, { method: "DELETE" }),
};
